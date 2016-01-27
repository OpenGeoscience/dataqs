import glob
import json
import os
import datetime
from django.test import TestCase
from dataqs.usgs_quakes.usgs_quakes import USGSQuakeProcessor
import httpretty

script_dir = os.path.dirname(os.path.realpath(__file__))


class UsgsQuakesTest(TestCase):
    """
    Tests the dataqs.usgs_quakes module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        today = datetime.datetime.utcnow()
        self.edate = today.strftime("%Y-%m-%d")
        self.sdate = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.processor = USGSQuakeProcessor(edate=self.edate, sdate=self.sdate)
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        with open(os.path.join(
                script_dir, 'resources/test_quakes.json')) as inf:
            response = inf.read()
        dl_url = self.processor.base_url.format(
            self.processor.params['sdate'], self.processor.params['edate'])
        httpretty.register_uri(httpretty.GET, dl_url,
                               body=response)
        jsonfile = self.processor.download(dl_url,
                                           self.processor.prefix + '.rss')
        jsonpath = os.path.join(
            self.processor.tmp_dir, jsonfile)
        with open(jsonpath) as json_in:
            quakejson = json.load(json_in)
            self.assertTrue("features" in quakejson)

    def test_cleanup(self):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        with open(os.path.join(
                script_dir, 'resources/test_quakes.json')) as inf:
            response = inf.read()
        dl_url = self.processor.base_url.format(
            self.processor.params['sdate'], self.processor.params['edate'])
        httpretty.register_uri(httpretty.GET, dl_url,
                               body=response)
        self.processor.download(dl_url, self.processor.prefix + '.rss')
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
