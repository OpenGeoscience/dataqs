import glob
import zipfile
import os
import datetime
from django.test import TestCase
import re
from dataqs.gfms.gfms import GFMSProcessor
import httpretty

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_mock_image():
    """
    Return a canned GFMS test image
    """
    zf = zipfile.ZipFile(os.path.join(script_dir,
                                      'resources/test_gfms.zip'))

    return zf.read('test_gfms.bin')


class GFMSTest(TestCase):
    """
    Tests the dataqs.gfms module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = GFMSProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

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
        month = today.strftime("%m")
        year = today.strftime("%Y")
        day = today.strftime("%d")
        imgs_url = self.processor.base_url + "{year}/{year}{month}".format(
            year=year, month=month)
        mock_imgs = ['<a href="Flood_byStor_{}{}{}{:02d}.bin"></a>'.format(
            year, month, day, i) for i in range(23)]
        httpretty.register_uri(httpretty.GET, imgs_url,
                               body='\n'.join(mock_imgs))
        img = self.processor.get_latest_future()
        date_match = re.search('\d{10}', img)
        self.assertIsNotNone(date_match)
        future_date = datetime.datetime.strptime(
            date_match.group(), '%Y%m%d%H')
        self.assertGreater(future_date, today)

    def test_download(self):
        """
        Verify that a file is downloaded
        """
        current_url = self.processor.get_most_current()
        httpretty.register_uri(httpretty.GET, current_url,
                               body=get_mock_image())
        imgfile = self.processor.download(current_url)
        self.assertTrue(os.path.exists(
            os.path.join(self.processor.tmp_dir, imgfile)))

    def test_convert_image(self):
        current_url = self.processor.get_most_current()
        httpretty.register_uri(httpretty.GET, current_url,
                               body=get_mock_image())
        imgfile = self.processor.download(current_url)
        tif_file = self.processor.convert(imgfile)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, tif_file)))

    def test_cleanup(self):
        current_url = self.processor.get_most_current()
        httpretty.register_uri(httpretty.GET, current_url,
                               body=get_mock_image())
        imgfile = self.processor.download(current_url)
        self.processor.convert(imgfile)
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
