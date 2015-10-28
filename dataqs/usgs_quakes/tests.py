import glob
import json
import os
import datetime
from django.test import TestCase
from dataqs.usgs_quakes.usgs_quakes import USGSQuakeProcessor


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

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        jsonfile = self.processor.download(self.processor.base_url.format(
            self.processor.params['sdate'], self.processor.params['edate']),
            self.processor.prefix + '.rss')
        jsonpath = os.path.join(
            self.processor.tmp_dir, jsonfile)
        self.assertTrue(os.path.exists(jsonpath))
        with open(jsonpath) as json_in:
            quakejson = json.load(json_in)
            self.assertTrue("features" in quakejson)

    def test_cleanup(self):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
