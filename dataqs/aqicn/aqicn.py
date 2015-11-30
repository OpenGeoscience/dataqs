#!/usr/local/bin/python
#Author:Bryan Roscoe
#https://github.com/bryanroscoe/aqicn
import json
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
from dataqs.helpers import postgres_query, get_html, layer_exists, table_exists
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
from geonode.geoserver.helpers import ogc_server_settings

REQ_HEADER={'User-Agent':
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 '
                'Safari/537.36'
            }

AQICN_SQL = u"""
DELETE FROM {table} where city = '{city}';
INSERT INTO {table}
(datetime, lat, lng, city, {keys}, country, country_name, the_geom)
 SELECT '{time}', {lat}, {lng}, '{city}', {val}, '{cntry}', '{cntry_name}',
 ST_GeomFromText('POINT({lng} {lat})') WHERE NOT EXISTS (
 SELECT 1 from {table} WHERE city = '{city}');
DELETE FROM {table}_archive where city = '{city}' and datetime = '{time}';
INSERT INTO {table}_archive
(datetime, lat, lng, city, {keys}, country, country_name, the_geom)
 SELECT '{time}', {lat}, {lng}, '{city}', {val}, '{cntry}', '{cntry_name}',
 ST_GeomFromText('POINT({lng} {lat})') WHERE NOT EXISTS (
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
  the_geom geometry,
  city character varying(256),
  datetime timestamp without time zone,
  country character varying(255),
  country_name character varying(255),
  CONSTRAINT {table}_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
CREATE INDEX {table}_city_idx ON {table}(city);
CREATE INDEX {table}_datetime_idx ON {table}(datetime);
CREATE INDEX {table}_the_geom ON {table} USING gist (the_geom);
"""


def thread_parse(table, html, cities, countries):
    aqi_parser = AQICNWorker(table, html, cities, countries)
    time.sleep(randint(0, 5))
    aqi_parser.run()


class AQICNWorker(object):
    def __init__(self, table, country_html, cities, countries):
        self.countrycities = country_html
        self.cities = cities
        self.prefix = table
        self.archive = self.prefix + "_archive"
        self.countries = countries
        if not table_exists(self.archive):
            postgres_query(AQICN_TABLE.format(table=self.archive), commit=True)

    def get_country(self, url):
        link = self.countrycities.find("a", href=url)
        if link:
            country_link = link.findPrevious('a', id=re.compile('.+'))
            if country_link:
                country_name = country_link.findNext('div').text.title()
                return country_link.get("id"), country_name
        return '', ''

    def handleCity(self, i, cityjson):
        try:
            print("\n\nScraping "+ cityjson["city"] , i+1, "of",
                  len(self.cities),
                  cityjson["g"], cityjson["x"])
            city = self.getUpdatedCity(cityjson)
            if city is None:
                return
            city['dateTime'] = self.getTime(city)
            #Get the details url from the popup
            city["popupURL"]=("http://aqicn.org/aqicn/json/mapinfo/@" +
                              str(city["x"]))

            print("Popup url is:", city["popupURL"])

            cityDetailPage = requests.get(city["popupURL"],
                                          timeout=60, headers=REQ_HEADER).text
            city["detailURL"] = re.search("http://aqicn\.org/[^\']*",
                                          cityDetailPage)

            if city["detailURL"]:
                city["detailURL"] = city["detailURL"].group(0)
                print("City Detail url is:", city["detailURL"])
                city['country'], city['country_name'] = \
                    self.get_country(city["detailURL"])

                if not self.countries or city['country'] in self.cities:
                    page = requests.get(city["detailURL"],
                                        timeout=60, headers=REQ_HEADER)
                    soup = bs(page.text, "lxml")
                    city["data"] = {}

                    curList = soup.find_all("td", {"id" : re.compile('^cur_')})
                    #Go on to the next city if we don't find anything
                    if not curList:
                        print("Nothing found for", city['city'])
                        return
                    #Loop through all the variables for this city
                    savedVars = ""
                    for cur in curList:
                        curId = cur['id']
                        savedVars += curId + ","
                        if type(cur.contents[0]).__name__ == 'Tag':
                            city['data'][curId] = cur.contents[0].text
                        else:
                            city['data'][curId] = cur.contents[0]
                    city['data']['cur_aqi'] = city['aqi']
                    self.saveData(city)

                    print("Saved", savedVars + "aqi", "for city", city['city'])
                else:
                    print ('{} not in countries {}'.format(
                        city['name'], str(self.countries)))
            else:
                print('Not found')
        except KeyboardInterrupt:
            sys.exit()
        except:
            print("encountered an error:", traceback.format_exc() )

    def saveData(self, city):
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
            city=city_name,
            keys=measurements,
            val=values,
            kv=kv,
            cntry=city['country'],
            cntry_name=city['country_name']

        ))
        postgres_query(sql_str, commit=True)

    def getUpdatedCity(self, city):
        for c in self.cities:
            if c["x"] == city["x"]:
                print("Matched cities for time update")
                print("Old", city)
                print("New", c)
                if c["city"] != city["city"]:
                    print("Whoops city is not the same")
                return c
        print("Whoops city not found")
        return None

    @staticmethod
    def getTime(city):
        long = str(city['g'][1])
        utime = city["utime"]
        print("Stripping time:", utime, ",", long);
        utime = utime.strip()
        utime = re.sub(r"on |\.|-", "", utime)
        print("Trying to parse time:", utime + " " + city["tz"]);
        try:
            cityTime = parse(utime + " " + city["tz"]).astimezone(tzutc());
        except:
            utime = re.sub(r"am$|pm$", "", utime)
            cityTime = parse(utime + " " + city["tz"]).astimezone(tzutc());

        print("Time parsed as:", cityTime);
        return cityTime

    def run(self):
        for i, city in enumerate(self.cities):
            try:
                int(city["x"])
            except:
                continue
            self.handleCity(i, city)
        print("End", datetime.datetime.now())


class AQICNProcessor(GeoDataProcessor):
    prefix = 'aqicn'
    directory = 'output'
    cities=None
    countries=None
    pool_size = 1
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

    def __init__(self, cities=None, countries=None):
        if cities:
            self.cities = cities
        else:
            self.cities = self.getCities()
        if countries:
            self.countries = []


    def download(self, url=None):
        if not url:
            url = self.base_url
        return get_html(url)

    def get_country_content(self):
        soup = bs(self.download(self.base_url), "lxml")
        return soup.find('div', class_='citytreehdr').findParent()

    @staticmethod
    def getCities():
        #First we must get the main map page
        print("Getting the cities")
        fullMap = requests.get("http://aqicn.org/map/world/",
                               timeout=60, headers=REQ_HEADER).text

        #Find the json embedded in the main page
        print("Finding the json")
        fullMapJsonString = re.search("(?<=mapInitWithData\()\[.*\](?=\))", fullMap)

        #Parse the json
        cities = None
        if fullMapJsonString:
            cities = json.loads(fullMapJsonString.group(0))
        return cities

    def process(self):
        datastore = ogc_server_settings.server.get('DATASTORE')
        if not layer_exists(self.prefix, datastore, DEFAULT_WORKSPACE):
            postgres_query(AQICN_TABLE.format(table=self.prefix), commit=True)

        print("Start" ,datetime.datetime.now())
        print("There are" ,len(self.cities) , "cities")
        pool = ThreadPool(self.pool_size)
        worker_html = self.get_country_content()
        for citylist in \
                [self.cities[i::self.pool_size] for i in xrange(len(self.cities))]:
            pool.apply(thread_parse, args=(
                self.prefix, worker_html, citylist, self.countries))
        pool.close()
        pool.join()

    def run(self):
        self.process()
        layer_name = self.prefix
        datastore = ogc_server_settings.server.get('DATASTORE')
        if not layer_exists(layer_name, datastore, DEFAULT_WORKSPACE):
            #self.create_view(layer)
            self.post_geoserver_vector(layer_name)
        self.update_geonode(layer_name,
                            title='Air Quality Index',
                            store=datastore)
        self.truncate_gs_cache(layer_name)
        self.cleanup()

if __name__ == '__main__':
    start = time.time()
    print start
    parser = AQICNProcessor(countries=['China', ])
    parser.run()
    end = time.time()
    print end
    print end-start
