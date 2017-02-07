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
import os
import logging
import time
import traceback
from django.conf import settings
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
from dataqs.helpers import ogr2ogr_exec, layer_exists, style_exists
from geonode.geoserver.helpers import ogc_server_settings

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class HIFLDProcessor(GeoDataProcessor):
    """
    Class for retrieving and processing layers from Homeland Infrastructure
    Foundation-Level Data (HIFLD), using the GeoJSON API.
    """
    prefix = 'hifld_'
    layers = []
    base_url = "https://hifld-dhs-gii.opendata.arcgis.com/datasets/"
    layer_category_mapping = {
        'us_state_boundaries': 'category:Boundaries',
        'us_county_boundaries': 'category:Boundaries',
        'us_urban_areas': 'category:Boundaries',
        'poultry_facilities': 'category:Agriculture',
        'state_fairgrounds': 'category:Agriculture',
        'epa_tsca_facilities': 'category:Chemicals',
        'epa_er_rmp_facilities': 'category:Chemicals',
        'epa_er_tri_facilities': 'category:Chemicals',
        'hospitals': 'category:Public Health',
        'pharmacies': 'category:Public Health',
        'hazmat_routes': 'category:Chemicals',
        'colleges_universities': 'category:Education',
        'nursing_homes': 'category:Public Health',
        'veterans_health_administration_medical_facilities': 'category:Public Health',
        'major_sport_venues': 'category:Public Venues',
        'day_care_centers': 'category:Education'
    }

    def __init__(self, layers=None):
        super(HIFLDProcessor, self).__init__()
        if layers:
            self.layers = layers
        else:
            self.layers = getattr(settings, 'HIFLD_LAYERS', [])

    def run(self):
        """
        Retrieve the layers and import into Geonode
        """

        for layer in self.layers:
            try:
                table = '{}{}'.format(self.prefix, layer['table'])
                lyr_file = os.path.join(self.tmp_dir,
                                        self.download(layer['url'],
                                                      filename=table))
                with open(lyr_file) as inf:
                    result = inf.readline(24)
                    if result.startswith('{"processingTime":'):
                        logger.info('Output is being generated,'
                                    'will try again in 60 seconds')
                        time.sleep(60)
                        lyr_file = os.path.join(
                            self.tmp_dir,
                            self.download(layer['url'], filename=table))
                db = ogc_server_settings.datastore_db
                ogr2ogr_exec("-overwrite -skipfailures -f PostgreSQL \
                    \"PG:host={db_host} user={db_user} password={db_pass} \
                    dbname={db_name}\" {lyr} -nln {table}".format(
                    db_host=db["HOST"],
                    db_user=db["USER"],
                    db_pass=db["PASSWORD"],
                    db_name=db["NAME"],
                    lyr="{}".format(lyr_file),
                    table=table))
                datastore = ogc_server_settings.server.get('DATASTORE')
                if not layer_exists(table, datastore, DEFAULT_WORKSPACE):
                    self.post_geoserver_vector(table)
                if not style_exists(table):
                    with open(os.path.join(
                            script_dir, 'resources/{}.sld'.format(
                            layer['sld']))) as sld:
                        sld_text = sld.read().format(table=layer['table'],
                                                     title=layer['name'])
                        self.set_default_style(table, table, sld_text)
                keywords = self.layer_category_mapping[layer['table']]
                self.update_geonode(
                    table,
                    title=layer['name'],
                    description=layer['description'],
                    store=datastore,
                    extra_keywords=[keywords])
                self.truncate_gs_cache(table)
            except Exception:
                logger.error('Error with layer {}'.format(layer['name']))
                logger.error(traceback.format_exc())
        self.cleanup()


if __name__ == '__main__':
    processor = HIFLDProcessor()
    processor.run()
