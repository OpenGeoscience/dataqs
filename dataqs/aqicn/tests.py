import json
import os
import datetime
from django.test import TestCase
import dataqs
from dataqs.aqicn.aqicn import AQICNProcessor
import httpretty
from mock import patch

script_dir = os.path.dirname(os.path.realpath(__file__))
tmpfile = os.path.join(script_dir, 'test_city.json')


def get_mock_response(filename):
    """
    Return a canned response with HTML for all cities
    """
    with open(os.path.join(
            script_dir, 'resources/{}'.format(filename))) as infile:
        return infile.read()


def mock_saveData(self, city):
    """
    Save data to a JSON file instead of to database
    """
    for key in city.keys():
        if isinstance(city[key], datetime.datetime):
            city[key] = city[key].strftime('%Y-%m-%d')
    with open(tmpfile, 'w') as outfile:
        outfile.write(json.dumps(city))


def mock_worker_init(self, table, cities):
    self.cities = cities
    self.prefix = table
    self.archive = self.prefix + "_archive"
    self.max_wait = 5


class AQICNTest(TestCase):
    """
    Tests the dataqs.aqicn module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = AQICNProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()

    def test_download(self):
        """
        Verify that the master url is retrieved.
        """
        httpretty.register_uri(
            httpretty.GET,
            self.processor.base_url,
            body=get_mock_response('test_aqicn_cities.html'),
            content_type='text/html')
        content = self.processor.download()
        self.assertIn(
            '<title>Air Pollution in the World - aqicn.org</title>', content)

    def test_getCities(self):
        """
        Verify that the processor creates a correct cities dictionary structure
        """
        self.processor.getCities()
        cities = self.processor.cities
        self.assertIsNotNone(cities)
        for city in cities:
            self.assertIsNotNone(city['city'], city)
            self.assertIsNotNone(city['country'], city)
            self.assertIsNotNone(city['url'], city)

    @patch('dataqs.aqicn.aqicn.AQICNWorker.__init__', mock_worker_init)
    @patch('dataqs.aqicn.aqicn.AQICNWorker.save_data', mock_saveData)
    def test_handleCity(self):
        """
        Verify that the correct AQI for a city is returned.
        """
        boston = u'http://aqicn.org/city/boston/'
        httpretty.register_uri(
            httpretty.GET,
            boston,
            body=get_mock_response('test_aqicn_boston.html'),
            content_type='text/html')
        cities = [{'city': u'Boston', 'country': u'USA', 'url': boston}]
        worker = dataqs.aqicn.aqicn.AQICNWorker('aqicn', cities)
        worker.handle_city(0, cities[0])
        with open(tmpfile) as jsonfile:
            city_json = json.load(jsonfile)
            self.assertEquals(city_json['data']['cur_aqi'], u'25')
            self.assertEquals(city_json['data']['cur_pm25'], u'25')
            self.assertEquals(city_json['data']['cur_o3'], u'11')
            self.assertEquals(city_json['data']['cur_so2'], u'2')
