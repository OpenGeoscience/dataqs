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

from __future__ import absolute_import

import logging
import os
import datetime
import re
import traceback

import requests
from dataqs.helpers import postgres_query, ogr2ogr_exec, \
    table_exists, purge_old_data, layer_exists, style_exists
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
import unicodecsv as csv
from geonode.geoserver.helpers import ogc_server_settings

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class WaterQualityPortalProcessor(GeoDataProcessor):
    """
    Class to process data from the The Water Quality Portal (WQP).
    Thw WQP is a cooperative service sponsored by the United States Geological
    Survey (USGS), the Environmental Protection Agency (EPA),
    and the National Water Quality Monitoring Council (NWQMC).
    """

    days = 30
    days_to_keep = 90
    indicators = ['pH',
                  'Oxygen',
                  'Temperature, water',
                  'Escherichia coli',
                  'Specific conductance',
                  'Turbidity',
                  'Phosphorus',
                  'Inorganic nitrogen (nitrate and nitrite)',
                  ]

    prefix = "wqp_api_"
    station_table = "wqp_api_stations"
    suffix = "_map"
    base_url = "http://www.waterqualitydata.us/{}/search?countrycode=US"
    description = (
        "Water quality measurements obtained from the Water Quality Data Portal"
        " (WQP), which includes data from:\n\nUSGS NWIS - Water-resources data "
        "collected from approximately 1.5 million sites in all 50 states, the "
        "District of Columbia, Puerto Rico, the Virgin Islands, Guam, American "
        "Samoa, and the Commonwealth of the Northern Mariana Islands.\n\nUSEPA "
        "STORET - A data warehouse for water quality, biological, and physical "
        "data used by state environmental agencies, EPA, other federal agencies"
        ", universities, private citizens, and others.\n\nSource: "
        "http://www.waterqualitydata.us"
    )
    skip_errors = True

    def __init__(self, *args, **kwargs):
        super(WaterQualityPortalProcessor, self).__init__(*args, **kwargs)
        if 'indicators' in kwargs.keys():
            self.indicators = kwargs['indicators']
        if 'days_to_keep' in kwargs.keys():
            self.days_to_keep = kwargs['days_to_keep']

    def update_station_table(self, csvfile):
        """
        Insert data on water quality monitoring stations
        from a csv file into the database
        :param csvfile: CSV file containing station data
        :return: None
        """
        vrt_content = (
            """<OGRVRTDataSource>
                <OGRVRTLayer name="{name}">
                    <SrcDataSource>{csv}</SrcDataSource>
                    <GeometryType>wkbPoint</GeometryType>
                    <LayerSRS>WGS84</LayerSRS>
                    <GeometryField encoding="PointFromColumns"
                    x="LongitudeMeasure" y="LatitudeMeasure"/>
                </OGRVRTLayer>
            </OGRVRTDataSource>
            """)
        station_table = self.station_table
        needs_index = not table_exists(station_table)

        db = ogc_server_settings.datastore_db
        vrt_file = os.path.join(self.tmp_dir, csvfile.replace('.csv', '.vrt'))
        csv_name = os.path.basename(csvfile).replace(".csv", "")
        if not os.path.exists(vrt_file):
            with open(vrt_file, 'w') as vrt:
                vrt.write(vrt_content.format(
                    name=csv_name, csv=os.path.join(self.tmp_dir, csvfile)))
        ogr2ogr_exec("-append -skipfailures -f PostgreSQL \
            \"PG:host={db_host} user={db_user} password={db_pass} \
            dbname={db_name}\" {vrt} -nln {table}".format(
            db_host=db["HOST"], db_user=db["USER"], db_pass=db["PASSWORD"],
            db_name=db["NAME"], vrt="{}".format(vrt_file), table=station_table))
        if needs_index:
            sql = 'ALTER TABLE {} '.format(station_table) + \
                  'ADD CONSTRAINT monitoringlocationidentifier_key ' + \
                  'UNIQUE (monitoringlocationidentifier)'
            logger.debug(sql)
            postgres_query(sql, commit=True)

    def create_indicator_table(self, indicator):
        """
        Create a database table for the given water quality indicator
        :param indicator: table name for the indicator
        :return: None
        """
        with open(os.path.join(script_dir,
                               'resources/create_table.sql')) as sql:
            postgres_query(sql.read().format(tablename=indicator), commit=True)

    def update_indicator_table(self, csvfile):
        """
        Insert water quality measurement data from a csv file
        into the appropriate indicator database table.
        :param csvfile: CSV file containing measurement data
        :return: None
        """
        date_cols = ("ActivityStartDate", "ActivityEndDate")
        indicator = csvfile.replace('_Result.csv', '')
        if not table_exists(indicator):
            self.create_indicator_table(indicator)
        with open(os.path.join(self.tmp_dir, csvfile), 'r') as csvin:
            csvreader = csv.reader(csvin)
            headers = None
            for row in csvreader:
                if not headers:
                    headers = ['"{}"'.format(x.replace('/', '_')) for x in row]
                else:
                    insert_sql = 'INSERT INTO "{}" ({}) SELECT \n'.format(
                        indicator,
                        ','.join(headers)
                    )
                    query_format = []
                    for i, val in enumerate(row):
                        attribute = headers[i].strip('"')
                        id_idx = headers.index('"ActivityIdentifier"')
                        query_format.append("%s")
                        if attribute in date_cols and val:
                            time_idx = headers.index(
                                '"{}_Time"'.format(
                                    attribute.replace("Date", "Time")))
                            zone_idx = headers.index(
                                '"{}_TimeZoneCode"'.format(
                                    attribute.replace("Date", "Time")))
                            time_str = "{} {} {}".format(
                                val, row[time_idx], row[zone_idx])
                            row[i] = time_str
                        else:
                            if not val or val == '.' or val == 'None':
                                row[i] = None
                    insert_sql += '{}'.format(
                        ','.join('{}'.format(x) for x in query_format)) + \
                        ' WHERE NOT EXISTS (SELECT 1 from ' + \
                        '{} WHERE "ActivityIdentifier" = \'{}\');'.format(
                            indicator, re.sub('\'{1}', '\'\'', row[id_idx]))
                    try:
                        postgres_query(
                            insert_sql, params=tuple(row), commit=True)
                    except Exception as e:
                        logger.error("The query failed: {} with parameters: {}".
                                     format(insert_sql, row))
                        logger.error(traceback.format_exc())
                        if not self.skip_errors:
                            raise e
        purge_old_data(indicator, date_cols[0], self.days_to_keep)
        if not table_exists(indicator + self.suffix):
            view_sql = 'CREATE OR REPLACE VIEW ' + indicator + self.suffix + \
                ' AS SELECT i.*, g.wkb_geometry from ' + indicator + ' i ' + \
                ' INNER JOIN ' + self.station_table + ' g on ' + \
                ' i."MonitoringLocationIdentifier" = ' + \
                ' g.monitoringlocationidentifier;'
            postgres_query(view_sql, commit=True)
            self.post_geoserver_vector(indicator + self.suffix)

    def safe_name(self, indicator):
        """
        Remove special characters from indicator names
        :param indicator:
        :return:
        """
        return re.sub('[\(\),]', '', indicator).lower().replace(' ', '')

    def download(self, indicator):
        """
        Download separate CSV's for each water quality indicator.
        Use multiprocessing to download asynchrously.
        :param days:
        :return: dict of csv files
        """
        today = datetime.datetime.utcnow()
        start_date = today - datetime.timedelta(days=self.days)
        url_template = "{url}&startDateLo={start}&startDateHi={end}&" + \
                       "characteristicName={indicator}"
        csvs = {}

        for query_type in ('Station', 'Result'):
            indicator_url = url_template.format(
                url=self.base_url.format(query_type),
                start=start_date.strftime('%m-%d-%Y'),
                end=today.strftime('%m-%d-%Y'),
                indicator=indicator)

            r = requests.get(indicator_url,
                             timeout=120, stream=True, verify=False)
            r.raise_for_status()
            outname = "{}{}_{}.csv".format(
                self.prefix, self.safe_name(indicator), query_type)
            outfile = os.path.join(self.tmp_dir, outname)

            with open(outfile, 'w') as outcsv:
                outcsv.write(r.content)

            csvs[query_type] = outname
        return csvs

    def run(self):
        """
        Run the processor
        :return: None
        """
        for indicator in self.indicators:
            csv_dict = self.download(indicator)
            station_csv = csv_dict['Station']
            if os.path.getsize(os.path.join(self.tmp_dir, station_csv)) > 0:
                self.update_station_table(station_csv)
            result_csv = csv_dict['Result']
            datastore = ogc_server_settings.server.get('DATASTORE')
            if os.path.getsize(os.path.join(self.tmp_dir, result_csv)) > 0:
                self.update_indicator_table(result_csv)
                layer_name = '{}{}{}'.format(self.prefix,
                                             self.safe_name(indicator),
                                             self.suffix)
                layer_title = 'Water Quality - {} - Updated {}'.format(
                    indicator, datetime.datetime.now().strftime('%Y-%m-%d'))
                if not layer_exists(layer_name,
                                    datastore,
                                    DEFAULT_WORKSPACE):
                    self.post_geoserver_vector(layer_name)
                if not style_exists(layer_name):
                    with open(os.path.join(
                            script_dir,
                            'resources/{}.sld'.format(layer_name))) as sld:
                        self.set_default_style(layer_name, layer_name,
                                               sld.read())
                self.update_geonode(layer_name,
                                    title=layer_title,
                                    description=self.description,
                                    store=datastore,
                                    extra_keywords=['category:Water Quality'])
                self.truncate_gs_cache(layer_name)
        self.cleanup()


if __name__ == '__main__':
    processor = WaterQualityPortalProcessor()
    processor.run()
