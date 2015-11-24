import glob
import json
import os
import datetime
from django.test import TestCase
from dataqs.gdacs.gdacs import GDACSProcessor


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
        self.processor = GDACSProcessor(edate=self.edate, sdate=self.sdate)

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        rssfile = self.processor.download(self.processor.base_url.format(
            self.processor.params['sdate'], self.processor.params['edate']))
        rsspath = os.path.join(
            self.processor.tmp_dir, rssfile)
        self.assertTrue(os.path.exists(rsspath))

    def test_cleanup(self):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
