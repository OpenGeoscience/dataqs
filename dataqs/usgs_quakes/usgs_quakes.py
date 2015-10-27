from __future__ import absolute_import
import json

import os
import datetime
import logging
from django.db import connections
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
from dataqs.helpers import postgres_query, ogr2ogr_exec, layer_exists
from geonode.geoserver.helpers import ogc_server_settings

logger = logging.getLogger("dataqs.processors")


class USGSQuakeProcessor(GeoDataProcessor):
    """
    Class for retrieving and processing the latest earthquake data from USGS.
    4 layers are created/updated with the same data (last 7 days by default),
    then any old data beyond the layer's time window (7 days, 30 days, etc)
    are removed.
    """

    tables = ("quakes_weekly", "quakes_monthly", "quakes_yearly", "quakes_archive")
    titles = ("Last 7 Days", "Last 30 Days", "Last 365 Days", "Archive")
    base_url = "http://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={}&endtime={}"
    params = {}

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

        super(USGSQuakeProcessor, self).__init__(*args)

    def purge_old_data(self):
        """
        Remove old data from weekly, monthly, and yearly PostGIS tables
        """
        today = datetime.date.today()
        last_week = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        last_month = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        last_year = (today - datetime.timedelta(days=365)).strftime("%Y-%m-%d")

        for interval, table in zip([last_week, last_month, last_year],
                                   self.tables):
            postgres_query(
                "DELETE FROM {} where CAST(time as timestamp) < '{}';".format(
                    table, interval), commit=True)

    def run(self, rss_file=None):
        """
        Retrieve the latest USGS earthquake data and append to all PostGIS
        earthquake tables, then remove old data
        :return:
        """
        if not rss_file:
            rss = self.download(self.base_url.format(self.params['sdate'],
                                                  self.params['edate']))
            rss_file = os.path.join(self.tmp_dir, rss)

        json_data = None
        with open(rss_file) as json_file:
            json_data = json.load(json_file)
            for feature in json_data['features']:
                time_original = datetime.datetime.utcfromtimestamp(
                    feature['properties']['time']/1000)
                updated_original = datetime.datetime.utcfromtimestamp(
                    feature['properties']['updated']/1000)
                feature['properties']['time'] = time_original.strftime(
                    "%Y-%m-%d %H:%M:%S")
                feature['properties']['updated'] = updated_original.strftime(
                    "%Y-%m-%d %H:%M:%S")
        with open(rss_file, 'w') as modified_file:
            json.dump(json_data, modified_file)

        db = ogc_server_settings.datastore_db
        for table, title in zip(self.tables, self.titles):
            ogr2ogr_exec("-append -skipfailures -f PostgreSQL \
                \"PG:host={db_host} user={db_user} password={db_pass} \
                dbname={db_name}\" {rss} -nln {table}".format(
                db_host=db["HOST"], db_user=db["USER"], db_pass=db["PASSWORD"],
                db_name=db["NAME"], rss="{}".format(rss_file), table=table))

            if not layer_exists(table,
                            ogc_server_settings.server.get('DATASTORE'),
                            DEFAULT_WORKSPACE):
                c = connections['datastore'].cursor()
                try:
                    c.execute(
                        'ALTER TABLE {tb} ADD CONSTRAINT {tb}_ids UNIQUE (ids);'.
                            format(tb=table))
                except:
                    c.close()
                self.post_geoserver_vector(table)
            self.update_geonode(table, title="Earthquakes - {}".format(title))
            self.truncate_gs_cache(table)
        self.purge_old_data()


if __name__ == '__main__':
    processor = USGSQuakeProcessor()
    processor.run()
