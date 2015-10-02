import glob
import os
import datetime
from django.test import TestCase
from dataqs.airnow.airnow import AirNowGRIB2HourlyProcessor


class AirNowTest(TestCase):
    """
    Tests the dataqs.airnow module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = AirNowGRIB2HourlyProcessor()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        files = self.processor.download()
        self.testfile = files[0]
        # Should be 3 files for 1 day
        self.assertEquals(3, len(files))
        # Make sure files exist in the right place
        for img in files:
            self.assertTrue(os.path.exists(os.path.join(
                self.processor.tmp_dir, img)))

    def test_download_multiple_days(self):
        """
        Verify that files are downloaded for multiple days.
        """
        files = self.processor.download(days=3)
        # Should be 3 files per day == 9 files
        self.assertEquals(9, len(files))
        # Make sure files exist in the right place
        for img in files:
            self.assertTrue(os.path.exists(os.path.join(
                self.processor.tmp_dir, img)))

    def test_parse_name(self):
        title, name, imgtime = self.processor.parse_name('US-15100215.grib2')
        self.assertEquals(
            'AirNow Hourly Air Quality Index (Ozone) - 2015-10-02 15:00 UTC',
            title)
        self.assertEquals('airnow_aqi_ozone', name)
        self.assertEquals(datetime.datetime(2015, 10, 2, 15, 0), imgtime)

    def test_convert_image(self):
        files = self.processor.download()
        title, name, imgtime = self.processor.parse_name(files[0])
        tif_file = self.processor.convert(files[0], imgtime, name)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, tif_file)))

    def test_cleanup(self):
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
