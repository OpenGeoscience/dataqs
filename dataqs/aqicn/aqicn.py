import json
import logging
import os
import sys
import re
import time
from multiprocessing.pool import ThreadPool
from random import randint

import requests
from bs4 import BeautifulSoup as bs
import datetime
import traceback
from dateutil.parser import parse
from dateutil.tz import tzutc
from dataqs.helpers import postgres_query, layer_exists, table_exists, \
    style_exists, asciier
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
from geonode.geoserver.helpers import ogc_server_settings

logger = logging.getLogger("dataqs.processors")

script_dir = os.path.dirname(os.path.realpath(__file__))

REQ_HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;'
              'q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 '
                  'Safari/537.36'
}

AQICN_SQL = u"""
DELETE FROM {table} where city = '{city}';
INSERT INTO {table}
(datetime, lat, lng, city, {keys}, country, the_geom)
 SELECT '{time}', {lat}, {lng}, '{city}', {val}, '{cntry}',
 ST_GeomFromText('POINT({lng} {lat})',4326) WHERE NOT EXISTS (
 SELECT 1 from {table} WHERE city = '{city}');
DELETE FROM {table}_archive where city = '{city}' and datetime = '{time}';
INSERT INTO {table}_archive
(datetime, lat, lng, city, {keys}, country, the_geom)
 SELECT '{time}', {lat}, {lng}, '{city}', {val}, '{cntry}',
 ST_GeomFromText('POINT({lng} {lat})',4326) WHERE NOT EXISTS (
 SELECT 1 from {table}_archive WHERE city = '{city}' and datetime = '{time}');
"""

AQICN_TABLE = u"""
CREATE TABLE IF NOT EXISTS {table}
(
  id serial NOT NULL,
  lat double precision,
  lng double precision,
  aqi integer,
  co integer,
  d integer,
  h integer,
  no2 integer,
  o3 integer,
  p integer,
  pm10 integer,
  pm25 integer,
  r integer,
  so2 integer,
  t integer,
  uvi integer,
  w integer,
  city character varying(256),
  datetime timestamp without time zone,
  country character varying(255),
  CONSTRAINT {table}_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
CREATE INDEX {table}_city_idx ON {table}(city);
CREATE INDEX {table}_datetime_idx ON {table}(datetime);
SELECT AddGeometryColumn ('public','{table}','the_geom',4326,'POINT',2);
CREATE INDEX {table}_the_geom ON {table} USING gist (the_geom);
"""


def thread_parse(table, cities):
    """
    Thread worker for a list of cities
    """
    aqi_parser = AQICNWorker(table, cities)
    aqi_parser.run()


class AQICNWorker(object):
    def __init__(self, table, cities):
        self.cities = cities
        self.prefix = table
        self.archive = self.prefix + "_archive"
        self.max_wait = 5
        if not table_exists(self.archive):
            postgres_query(AQICN_TABLE.format(table=self.archive), commit=True)

    def handle_city(self, i, city):
        try:
            logger.debug('Scraping %d of %d cities - %s' % (
                i+1, len(self.cities), city['url']))
            time.sleep(randint(1, self.max_wait))
            page = requests.get(city['url'], timeout=60, headers=REQ_HEADER)
            page.raise_for_status()
            soup = bs(page.text, "lxml")

            aqi_div = soup.find('div', class_='aqivalue')
            if not aqi_div:
                logger.error('No AQI for {}'.format(city['url']))
                return
            aqi = aqi_div.text
            if not aqi.isdigit():
                logger.error('AQI is not a number - {}'.format(city['url']))
                return

            time_div = soup.find('span', id=re.compile(r'aqiwgtutime.*'))
            if time_div:
                city['utime'] = time_div.text
            else:
                logger.error('No date/time: {}'.format(city['url']))
                return

            map_string = re.search(
                '(?<=mapInitWithData\()\[\{[^;]*\}\]', soup.text).group(0)
            map_json = json.loads(map_string.strip('\n'))
            for item in map_json:
                if re.search(u'{}(,|$)'.format(asciier(city['city']).lower()),
                             asciier(item['city']).lower()):
                    for key in ['tz', 'g']:
                        city[key] = item[key]
                    break
            if 'utime' not in city:
                logger.error('No data for {}'.format(city['url']))
                return
            city['dateTime'] = self.get_time(city)
            city["data"] = {}
            cur_list = soup.find_all("td", {"id": re.compile('^cur_')})
            # Go on to the next city if we don't find anything
            if not cur_list:
                logger.debug("Nothing found for %s" % city['city'])
                return
            # Loop through all the variables for this city
            saved_vars = ""
            for cur in cur_list:
                curId = cur['id']
                saved_vars += curId + ","
                if type(cur.contents[0]).__name__ == 'Tag':
                    city['data'][curId] = cur.contents[0].text
                else:
                    city['data'][curId] = cur.contents[0]
            city['data']['cur_aqi'] = aqi
            self.save_data(city)
            logger.debug("Saved %s aqi for city %s" % (
                saved_vars, city['city']))
            # Clear out the city to reduce memory footprint
            for key in city.keys():
                city.pop(key, None)

        except KeyboardInterrupt:
            sys.exit()
        except Exception:
            logger.error('Error with city {}'.format(city['url']))
            logger.error(traceback.format_exc())

    def save_data(self, city):
        for item in city['data']:
            if city['data'][item] == '-':
                city['data'][item] = 'NULL'
        measurements = ','.join(x[4:] for x in city['data'].keys())
        values = ','.join(
            [x for x in city['data'].values()])
        city_name = unicode(city['city'])
        kv = ','.join(['{} = {}'.format(k, v) for k, v in zip(
            [x[4:] for x in city['data'].keys()],
            [x for x in city['data'].values()]
        )])
        sql_str = unicode(AQICN_SQL.format(
            table=self.prefix,
            time=city['dateTime'].strftime('%Y-%m-%d %H:%M:%S'),
            lat=city['g'][0],
            lng=city['g'][1],
            city=city_name.replace('\'', '\'\''),
            keys=measurements,
            val=values,
            kv=kv,
            cntry=city['country']
        ))
        postgres_query(sql_str, commit=True)

    @staticmethod
    def get_time(city):
        try:
            utime = city["utime"]
            utime = utime.strip()
            utime = re.sub(r"Updated on |\.|-", "", utime)
            logger.debug("Trying to parse time: %s , %s" % (
                str(utime), city["tz"]))
            try:
                city_time = parse(utime + " " + city["tz"]).astimezone(tzutc())
            except:
                utime = re.sub(r"am$|pm$", "", utime)
                city_time = parse(utime + " " + city["tz"]).astimezone(tzutc())

            logger.debug("Time parsed as: %s", str(city_time))
        except Exception as e:
            logger.error(city)
            raise e
        return city_time

    def run(self):
        for i, city in enumerate(self.cities):
            if 'url' in city:
                self.handle_city(i, city)
            else:
                logger.warn('No url for {}'.format(city))
        logger.debug("End %s" % str(datetime.datetime.now()))


class AQICNProcessor(GeoDataProcessor):
    prefix = 'aqicn'
    directory = 'output'
    cities = None
    countries = None
    pool_size = 6
    base_url = 'http://aqicn.org/city/all/'
    layers = {
        'aqi': 'Air Quality Index',
        'co': 'Carbon Monoxide',
        'd': 'Dew',
        'h': 'Humidity',
        'no2': 'Nitrogen Dioxide',
        'o3': 'Ozone',
        'p': 'Atmospheric Pressure',
        'pm25': 'Particulate Matter (PM25)',
        'pm10': 'Particulate Matter (PM10)',
        'r': 'Rain',
        'so2': 'Sulfur Dioxide',
        't': 'Temperature (celcius)',
        'uvi': 'Ultraviolet Index',
        'w': 'Wind Speed'
    }

    def __init__(self, countries=None, cities=None):
        super(AQICNProcessor, self).__init__()
        if not countries:
            self.countries = []
        else:
            self.countries = countries
        if not cities:
            self.cities = []
        else:
            self.cities = cities

    def download(self, url=None):
        if not url:
            url = self.base_url
        return super(AQICNProcessor, self).download(url, html=True)

    def getCities(self):
        soup = bs(self.download(self.base_url), "lxml")
        city_div = soup.find('div', class_='citytreehdr').findParent()

        countries = city_div.find_all('a', id=re.compile("^.+"))

        for country in countries:
            country_code = country.get('id')
            if not self.countries or country.get("id") in self.countries:
                citylink = country.findNext('a')
                while citylink and citylink.get('id') is None and citylink.text:
                    self.cities.append({
                        'city': citylink.text,
                        'country': country_code,
                        'url': citylink.get('href')})
                    citylink = citylink.findNext('a')

    def split_list(self, num):
        """ Yield n successive lists from cities list.
        """
        newn = int(1.0 * len(self.cities) / num + 0.5)
        for i in xrange(0, num-1):
            yield self.cities[i*newn:i*newn+newn]
        yield self.cities[num*newn-newn:]

    def process(self):
        if not table_exists(self.prefix):
            postgres_query(AQICN_TABLE.format(table=self.prefix), commit=True)
        logger.debug("Start %s" % datetime.datetime.now())
        if not self.cities:
            self.getCities()
        logger.debug("There are %s cities" % str(len(self.cities)))
        pool = ThreadPool(self.pool_size)
        for citylist in self.split_list(self.pool_size):
            pool.apply_async(thread_parse, args=(self.prefix, citylist))
        pool.close()
        pool.join()

    def run(self):
        self.process()
        layer_name = self.prefix
        datastore = ogc_server_settings.server.get('DATASTORE')
        if not layer_exists(layer_name, datastore, DEFAULT_WORKSPACE):
            self.post_geoserver_vector(layer_name)
        if not style_exists(layer_name):
            with open(os.path.join(script_dir, 'resources/aqicn.sld')) as sld:
                self.set_default_style(layer_name, layer_name, sld.read())
        self.update_geonode(layer_name,
                            title='Air Quality Index',
                            store=datastore)
        self.truncate_gs_cache(layer_name)
        self.cleanup()

if __name__ == '__main__':
    parser = AQICNProcessor()
    parser.run()
