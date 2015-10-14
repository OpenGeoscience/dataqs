import glob
import os
import datetime
from urlparse import urljoin
from django.test import TestCase
from dataqs.forecastio.forecastio_air import ForecastIOAirTempProcessor


class ForecastIOAirTempTest(TestCase):
    """
    Tests the dataqs.forecastio module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = ForecastIOAirTempProcessor()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        today = datetime.datetime.utcnow()
        strmonth, strday, strhour = (
            '{0:02d}'.format(x) for x in [today.month, today.day, today.hour])
        imgfile = self.processor.download(urljoin(
            self.processor.base_url, '{}/{}/{}/{}.tif'.format(
                today.year, strmonth, strday, strhour)))
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
        today = datetime.datetime.utcnow()
        strmonth, strday, strhour = (
            '{0:02d}'.format(x) for x in [today.month, today.day, today.hour])
        imgfile = self.processor.download(urljoin(
            self.processor.base_url, '{}/{}/{}/{}.tif'.format(
                today.year, strmonth, strday, strhour)))
        tif_file = self.processor.convert(imgfile, today)
        self.assertTrue(tif_file.endswith('0000000Z.tif'))
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, tif_file)))

    def test_cleanup(self):
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))