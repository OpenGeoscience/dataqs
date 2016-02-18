import glob
import zipfile
import os
import datetime
from urlparse import urljoin
from django.test import TestCase
from dataqs.forecastio.forecastio_air import ForecastIOAirTempProcessor
import httpretty

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_test_image():
    """
    Return a canned response with HTML for Boston
    """
    zf = zipfile.ZipFile(os.path.join(script_dir,
                                      'resources/test_forecastio.zip'))

    return zf.read('test_forecastio.tif')


class ForecastIOAirTempTest(TestCase):
    """
    Tests the dataqs.forecastio module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = ForecastIOAirTempProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        today = datetime.datetime.utcnow()
        strmonth, strday, strhour = (
            '{0:02d}'.format(x) for x in [today.month, today.day, today.hour])
        img_url = urljoin(self.processor.base_url, '{}/{}/{}/{}.tif'.format(
            today.year, strmonth, strday, strhour))
        raw_name = "{prefix}_{hour}.tif".format(
            prefix=self.processor.prefix,
            hour='{0:02d}'.format(today.hour))
        httpretty.register_uri(httpretty.GET, img_url,
                               body=get_test_image(),
                               content_type="image/tif")
        imgfile = self.processor.download(img_url, filename=raw_name)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, imgfile)))

    def test_parse_name(self):
        """
        Layer title should contain date of image
        :return:
        """
        today = datetime.datetime(2006, 11, 21, 16, 00)
        title = self.processor.parse_name(today)
        self.assertEquals(
            'Global (near-surface) Air Temperature - 2006-11-21 16:00 UTC',
            title)

    def test_convert_image(self):
        """
        Verifies that the original image is translated into a new one with the
        expected name and location.
        :return:
        """
        today = datetime.datetime.utcnow()
        strmonth, strday, strhour = (
            '{0:02d}'.format(x) for x in [today.month, today.day, today.hour])
        img_url = urljoin(self.processor.base_url, '{}/{}/{}/{}.tif'.format(
            today.year, strmonth, strday, strhour))
        raw_name = "{prefix}_{hour}.tif".format(
            prefix=self.processor.prefix,
            hour='{0:02d}'.format(today.hour))
        httpretty.register_uri(httpretty.GET, img_url,
                               body=get_test_image(),
                               content_type="image/tif")
        imgfile = self.processor.download(img_url, filename=raw_name)
        tif_file = self.processor.convert(imgfile, today)
        self.assertTrue(tif_file.endswith('0000000Z.tif'))
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, tif_file)))

    def test_cleanup(self):
        """
        Verifies that no images are left over after cleanup
        :return:
        """
        today = datetime.datetime.utcnow()
        strmonth, strday, strhour = (
            '{0:02d}'.format(x) for x in [today.month, today.day, today.hour])
        img_url = urljoin(self.processor.base_url, '{}/{}/{}/{}.tif'.format(
            today.year, strmonth, strday, strhour))
        raw_name = "{prefix}_{hour}.tif".format(
            prefix=self.processor.prefix,
            hour='{0:02d}'.format(today.hour))
        httpretty.register_uri(httpretty.GET, img_url,
                               body=get_test_image(),
                               content_type="image/tif")
        self.processor.download(img_url, filename=raw_name)
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))

