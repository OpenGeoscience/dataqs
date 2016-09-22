import glob
import os
import unittest
from datetime import date
from django.test import TestCase
from dataqs.cmap.cmap import CMAPProcessor

script_dir = os.path.dirname(os.path.realpath(__file__))


class CMAPPTest(TestCase):
    """
    Tests the dataqs.cmap module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = CMAPProcessor()
        self.dl_file = os.path.join(script_dir, 'resources/cmap.nc')

    def tearDown(self):
        self.processor.cleanup()

    def test_convert(self):
        """
        Verify that a NetCDF file is converted via netcdf and cdo apps.
        Skip if these apps are not installed.
        """
        try:
            converted_nc = self.processor.convert(self.dl_file)
            self.assertTrue(os.path.exists(converted_nc))
        except OSError:
            # cdo and/or netcdf not installed
            raise unittest.SkipTest()

    def test_extract_band(self):
        """
        Verify that a GeoTIFF file is created.
        """
        dl_tif = self.processor.extract_band(
            self.dl_file, 1, os.path.join(self.processor.tmp_dir, 'cmap.tif'))
        self.assertTrue(os.path.exists(dl_tif))

    def test_get_title(self):
        """
        Verify that the correct title is returned
        """
        title = self.processor.get_title(451)
        self.assertEquals(
            'CPC Merged Analysis of Precipitation, 1979/01 - 2016/07', title)

    def test_get_date(self):
        """
        Verify that the correct date is returned
        """
        band_date = self.processor.get_date(451)
        self.assertEquals(band_date, date(2016, 7, 1))

    def test_cleanup(self):
        """
        Make sure temporary files are deleted.
        """
        self.processor.extract_band(
            self.dl_file, 1, os.path.join(self.processor.tmp_dir, 'cmap.tif'))
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
