from __future__ import absolute_import

import logging
import os
import datetime
from django.db import connections
from geonode.geoserver.helpers import ogc_server_settings
from dataqs.helpers import ogr2ogr_exec, layer_exists, style_exists
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class GDACSProcessor(GeoDataProcessor):
    """
    Class for processing data from the Global Disaster Alerts &
    Coordination System website (http://gdacs.org/)
    """

    prefix = "gdacs_alerts"
    layer_title = 'Flood, Quake, Cyclone Alerts - GDACS'
    params = {}
    base_url = "http://www.gdacs.org/rss.aspx?profile=ARCHIVE&from={}&to={}"

    def __init__(self, *args, **kwargs):
        for key in kwargs.keys():
            self.params[key] = kwargs.get(key)

        if 'sdate' not in self.params:
            today = datetime.date.today()
            self.params['sdate'] = (
                today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")

        if 'edate' not in self.params:
            today = datetime.date.today()
            self.params['edate'] = today.strftime("%Y-%m-%d")

        super(GDACSProcessor, self).__init__(*args)

    def run(self):
        rss = self.download(self.base_url.format(
            self.params['sdate'], self.params['edate']), self.prefix + ".rss")
        db = ogc_server_settings.datastore_db
        ogr2ogr_exec("-append -skipfailures -f PostgreSQL \
            \"PG:host={db_host} user={db_user} password={db_pass} \
            dbname={db_name}\" {rss} -nln {table}".format(
            db_host=db["HOST"], db_user=db["USER"],
            db_pass=db["PASSWORD"], db_name=db["NAME"],
            rss="{}".format(os.path.join(self.tmp_dir, rss)),
            table=self.prefix))
        datastore = ogc_server_settings.server.get('DATASTORE')
        if not layer_exists(self.prefix, datastore, DEFAULT_WORKSPACE):
            c = connections[datastore].cursor()
            try:
                c.execute(
                    'ALTER TABLE {tb} ADD CONSTRAINT {tb}_guid UNIQUE (guid);'.
                    format(tb=self.prefix))
            except Exception as e:
                c.close()
                raise e
            self.post_geoserver_vector(self.prefix)
        if not style_exists(self.prefix):
            with open(os.path.join(
                    script_dir, 'resources/gdacs.sld')) as sld:
                self.set_default_style(self.prefix, self.prefix, sld.read())
        self.update_geonode(self.prefix, title=self.layer_title,
                            store=datastore)
        self.truncate_gs_cache(self.prefix)
        self.cleanup()

if __name__ == '__main__':
    processor = GDACSProcessor()
    processor.run()
