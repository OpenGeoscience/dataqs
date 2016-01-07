import glob
import os
import datetime
from urlparse import urljoin
from django.test import TestCase
from dataqs.aqicn.aqicn import AQICNProcessor


class AQICNTest(TestCase):
    """
    Tests the dataqs.aqicn module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = AQICNProcessor()

    def test_download(self):
        """
        Verify that the master url is retrieved.
        """
        content = self.processor.download()
        self.assertIn(
            '<title>Air Pollution in the World - aqicn.org</title>', content)

    def test_getCities(self):
        self.processor.getCities()
        cities = self.processor.cities
        self.assertIsNotNone(cities)
        for city in cities:
            self.assertIsNotNone(city['city'], city)
            self.assertIsNotNone(city['country'], city)
            self.assertIsNotNone(city['url'], city)
