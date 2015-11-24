import glob
import os
from django.test import TestCase
from dataqs.spei.spei import SPEIProcessor


class SpieTest(TestCase):
    """
    Tests the dataqs.spie module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = SPEIProcessor()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        imgfile = self.processor.download("{}spei03.nc".format(
            self.processor.base_url))
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, imgfile)))

    def test_convert_image(self):
        """
        Converted image should be create in temp directory
        :return:
        """
        dl_tif = self.processor.download("{}spei01.nc".format(
            self.processor.base_url))
        convert_tif = self.processor.convert(dl_tif)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, convert_tif)))

    def test_cleanup(self):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
