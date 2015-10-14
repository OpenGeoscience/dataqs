import glob
import os
import datetime
from urlparse import urljoin
from django.test import TestCase
import re
from dataqs.gfms.gfms import GFMSProcessor


class GFMSTest(TestCase):
    """
    Tests the dataqs.gfms module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = GFMSProcessor()

    def test_find_current(self):
        """
        Verify that current file is for today's date
        """
        today = datetime.datetime.utcnow()
        strmonth, strday = (
            '{0:02d}'.format(x) for x in [today.month, today.day])
        img = self.processor.get_most_current()
        date_str = '_{}{}{}'.format(today.year, strmonth, strday)
        self.assertTrue(date_str in img)

    def test_find_future(self):
        """
        Verify that future file is for a future date
        """
        today = datetime.datetime.now()
        img = self.processor.get_latest_future()
        date_match = re.search('\d{10}', img)
        self.assertIsNotNone(date_match)
        future_date = datetime.datetime.strptime(date_match.group(), '%Y%m%d%H')
        self.assertGreater(future_date, today)

    def test_download(self):
        """
        Verify that a file is downloaded
        """
        imgfile = self.processor.download(self.processor.get_most_current())
        self.assertTrue(os.path.exists(
            os.path.join(self.processor.tmp_dir, imgfile)))

    def test_convert_image(self):
        imgfile = self.processor.download(self.processor.get_most_current())
        tif_file = self.processor.convert(imgfile)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, tif_file)))

    def test_cleanup(self):
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))