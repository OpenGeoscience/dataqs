#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc. and Epidemico Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import json
import logging
import os
from datetime import datetime, date, timedelta
import re
from requests import HTTPError
import unicodecsv as csv
from dataqs.helpers import ogr2ogr_exec, layer_exists, style_exists, \
    postgres_query
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
from geonode.geoserver.helpers import ogc_server_settings

script_dir = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger("dataqs.processors")

# Indicate what columns in csv are latitude, longitude
vrt_content = ("""<OGRVRTDataSource>
    <OGRVRTLayer name="{name}">
        <SrcDataSource>{csv}</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <LayerSRS>WGS84</LayerSRS>
        <GeometryField encoding="PointFromColumns" x="lng" y="lat"/>
    </OGRVRTLayer>
</OGRVRTDataSource>
""")

# Column types for csv file
csvt_content = '"String","Real","Real","Integer","Integer","Integer",' \
               '"Integer","Integer","Integer","Integer","Date"'


class MortalityProcessor(GeoDataProcessor):
    """
    Downloads and transforms CDC Morbidity and Mortality Weekly Reports,
    then uploads to GeoNode as weekly and archived layers.
    """
    prefix = 'mmwr'
    base_title = 'Morbidity and Mortality Reports'
    titles = ['Weekly', 'Archive']
    base_url = 'http://wonder.cdc.gov/mmwr/mmwr_{year}.asp?request=Export' \
               '&mmwr_location=Click+here+for+all+Locations&mmwr_table=4A' \
               '&mmwr_year={year}&mmwr_week={week:02d}'
    params = {}
    description = (
        "Mortality data voluntarily reported from 122 cities in the United "
        "States, most of which have populations of 100,000 or more. A death is "
        "reported by the place of its occurrence and by the week that the death"
        " certificate was filed. Fetal deaths are not included.\n\nThe "
        "Morbidity and Mortality Weekly Report (MMWR ) series is prepared by "
        "the Centers for Disease Control and Prevention (CDC). Often called the"
        " voice of CDC,” the MMWR  series is the agency’s primary vehicle for "
        "scientific publication of timely, reliable, authoritative, accurate, "
        "objective, and useful public health information and recommendations. "
        "The data in the weekly MMWR  are provisional, based on weekly reports "
        "to CDC by state health departments.\n\nSource: http://wonder.cdc.gov/"
        "mmwr/mmwr_2015.asp"
    )

    def __init__(self, *args, **kwargs):
        for key in kwargs.keys():
            self.params[key] = kwargs.get(key)

        if 'sdate' not in self.params:
            today = date.today()
            self.params['sdate'] = today.strftime("%Y-%m-%d")

        if 'edate' not in self.params:
            today = date.today()
            self.params['edate'] = today.strftime("%Y-%m-%d")

        super(MortalityProcessor, self).__init__(*args)

    def generate_csv(self, report_date):
        """
        Create a csv file from MWWR text reports
        :param report_date: Date of report
        :return: None
        """
        csvfile = "{}.csv".format(self.prefix)
        week = report_date.isocalendar()[1]
        year = report_date.year
        logger.debug('Year {}, week {}'.format(year, week))
        exportfile = '{}.txt'.format(self.prefix)
        for x in range(4):
            try:
                exportfile = self.download(
                    self.base_url.format(
                        year=year, week=week), filename=exportfile)
                with open(
                        os.path.join(self.tmp_dir, exportfile)) as testfile:
                    content = testfile.read().strip()
                    if content.startswith('<'):
                        raise HTTPError
                    break
            except HTTPError:
                if x < 3:
                    year = year - 1 if week == 1 else year
                    week = week-1 if week > 1 else 52
                    logger.debug('Year {}, week {}'.format(year, week))
                else:
                    logger.error("Could not get year {} week {}".format(
                        year, week
                    ))
                    return

        with open(os.path.join(script_dir, 'resources/mmwr.json')) as jsonfile:
            places = json.load(jsonfile)

        with open(os.path.join(self.tmp_dir, exportfile)) as openfile:
            reader = csv.reader(openfile, delimiter='\t')

            with open(os.path.join(self.tmp_dir, csvfile), 'w') as outfile:
                writer = csv.writer(outfile)
                headers = ['place', 'lng', 'lat', 'all', 'a65', 'a45_64',
                           'a25_44', 'a01-24', 'a01', 'flu', 'report_date']
                writer.writerow(headers)
                report_date = None
                for row in reader:
                    if len(row) == 1 and not report_date:
                        datematch = re.search('week ending (.+)', row[0])
                        if datematch:
                            report_date = datetime.strptime(
                                datematch.group(1), '%B %d, %Y')
                            report_date = report_date.strftime('%Y-%m-%d')
                    if len(row) > 2:
                        place = row[0]
                        if place in places:
                            match = places[place]
                            row.insert(1, match[0])
                            row.insert(1, match[1])
                            row.insert(10, report_date)
                            writer.writerow(row)
                        elif place != 'TOTAL':
                            raise Exception(
                                'Could not find matching city: {}'.format(
                                    place))

    def update_layer(self, layer):
        """
        Create or update the MMWR layer in GeoNode
        :param layer: Layer to update (weekly or archive)
        :return: None
        """
        csvfile = "{}.csv".format(self.prefix)
        vrt_file = os.path.join(self.tmp_dir, '{}.vrt'.format(self.prefix))
        csvt_file = os.path.join(self.tmp_dir, '{}.csvt'.format(self.prefix))
        if not os.path.exists(vrt_file):
            with open(vrt_file, 'w') as vrt:
                vrt.write(vrt_content.format(
                    name=csvfile.replace('.csv', ''),
                    csv=os.path.join(self.tmp_dir, csvfile)))
        if not os.path.exists(csvt_file):
            with open(csvt_file, 'w') as csvt:
                csvt.write(csvt_content)

        db = ogc_server_settings.datastore_db
        table = '{}_{}'.format(self.prefix, layer).lower()
        option = 'overwrite' if layer.lower() == 'weekly' else 'append'
        ogr2ogr_exec("-{option} -skipfailures -f PostgreSQL \
            \"PG:host={db_host} user={db_user} password={db_pass} \
            dbname={db_name}\" {vrt} -nln {table}".format(
            db_host=db["HOST"], db_user=db["USER"],
            db_pass=db["PASSWORD"], db_name=db["NAME"],
            vrt="{}".format(vrt_file), option=option, table=table))
        if not layer_exists(table,
                            ogc_server_settings.server.get('DATASTORE'),
                            DEFAULT_WORKSPACE):
            constraint = 'ALTER TABLE {table} ADD CONSTRAINT ' \
                         '{table}_unique UNIQUE (place, report_date)'\
                .format(table=table)
            postgres_query(constraint, commit=True)
            self.post_geoserver_vector(table)
        if not style_exists(table):
            with open(os.path.join(
                    script_dir, 'resources/mmwr.sld')) as sldfile:
                sld = sldfile.read().format(layername=table)
                self.set_default_style(table, table, sld)
        self.update_geonode(
            table,
            title='{} {}'.format(self.base_title, layer),
            description=self.description,
            extra_keywords=['category:Population'])
        self.truncate_gs_cache(table)

    def run(self):
        """
        Download, transform, and upload MMWR data to GeoNode.
        :return: None
        """
        cur_date = datetime.strptime(self.params['edate'], '%Y-%m-%d')
        earliest_date = datetime.strptime(self.params['sdate'], '%Y-%m-%d')

        self.generate_csv(cur_date)
        self.update_layer(self.titles[0])

        while cur_date >= earliest_date:
            cur_date = cur_date - timedelta(days=7)
            self.generate_csv(cur_date)
            self.update_layer(self.titles[1])
        self.cleanup()

if __name__ == '__main__':
    processor = MortalityProcessor()
    processor.run()
