from __future__ import absolute_import

import logging
import os
import datetime
from django.db import connections
from geonode.geoserver.helpers import ogc_server_settings
from dataqs.helpers import ogr2ogr_exec, layer_exists
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE

logger = logging.getLogger("dataqs.processors")


class GDACSProcessor(GeoDataProcessor):
    """
    Class for processing data from the Global Disaster Alerts &
    Coordination System website (http://gdacs.org/)
    """

    layer_name = "gdacs_alerts"
    layer_title = 'Flood, Quake, Cyclone Alerts - GDACS'
    params={}

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
        rss = self.download(
            "http://www.gdacs.org/rss.aspx?profile=ARCHIVE&from={}&to={}".
                format(self.params['sdate'], self.params['edate']),
            filename="gdacs.rss")
        db = ogc_server_settings.datastore_db
        ogr2ogr_exec("-append -skipfailures -f PostgreSQL \
            \"PG:host={db_host} user={db_user} password={db_pass} \
            dbname={db_name}\" {rss} -nln {table}".format(db_host=db["HOST"],
                                       db_user=db["USER"],
                                       db_pass=db["PASSWORD"],
                                       db_name=db["NAME"],
                                       rss="{}".format(os.path.join(
                                           self.tmp_dir, rss)),
                                       table=self.layer_name))
        if not layer_exists(self.layer_name,
                            ogc_server_settings.server.get('DATASTORE'),
                            DEFAULT_WORKSPACE):
            c = connections['datastore'].cursor()
            try:
                c.execute(
                    'ALTER TABLE {tb} ADD CONSTRAINT {tb}_guid UNIQUE (guid);'.
                        format(tb=self.layer_name))
            except:
                c.close()
            self.post_geoserver_vector(self.layer_name)
        self.update_geonode(self.layer_name, title=self.layer_title)
        self.truncate_gs_cache(self.layer_name)


if __name__ == '__main__':
    processor = GDACSProcessor()
    processor.run()
