from __future__ import absolute_import
import json

import os
import datetime
import logging
from django.db import connections
from django.conf import settings
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
from dataqs.helpers import postgres_query, ogr2ogr_exec, layer_exists, \
    style_exists
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
                    result = inf.read()
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
                self.update_geonode(table,
                                    title=layer['name'],
                                    store=datastore)
                self.truncate_gs_cache(table)
            except Exception as e:
                logger.error('Error with layer {}'.format(layer['name']))
                logger.error(traceback.format_exc())
        self.cleanup()


if __name__ == '__main__':
    processor = HIFLDProcessor()
    processor.run()
