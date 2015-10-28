import glob
import os
import datetime
from django.test import TestCase
from dataqs.nasa_gpm.nasa_gpm import GPMProcessor


class NasaGpmTest(TestCase):
    """
    Tests the dataqs.nasa_gpm module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = GPMProcessor()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        today = datetime.datetime.utcnow()
        imgfile = self.processor.download()[0]
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, imgfile)))
        self.assertTrue('3B-HHR-E.MS.MRG.3IMERG.{}'.format(
            datetime.datetime.strftime(today, '%Y%m%d')) in imgfile)


    def test_parse_name(self):
        """
        Layer title should contain date of image
        :return:
        """
        imgfile = '3B-HHR-E.MS.MRG.3IMERG.20151027-S133000-E135959.0810.V03E.1day.tif'
        title = self.processor.parse_name(imgfile)[0]
        self.assertTrue('NASA Global Precipitation Estimate (1day) - 2015-10-27'
                       in title)

    def test_convert_image(self):
        """
        Converted image should be create in temp directory
        :return:
        """
        dl_tif = self.processor.download()[0]
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