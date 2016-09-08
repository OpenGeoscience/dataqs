import glob
import zipfile
import os
import datetime
from django.test import TestCase
from dataqs.nasa_gpm.nasa_gpm import GPMProcessor
from mock import patch

script_dir = os.path.dirname(os.path.realpath(__file__))


def mock_retrbinary(self, name, writer):
    """
    Mocks the ftplib.FTP.retrbinary method, writes test image to disk.
    """
    extension = name[-3:]
    zf = zipfile.ZipFile(os.path.join(script_dir, 'resources/test_gpm.zip'))
    writer(zf.read('test_gpm.{}'.format(extension)))
    return None


def mock_nlst(self, *args):
    """
    Mocks the ftplib.FTP.nlst method, returns a list of files based on date.
    """
    file_list = []
    current_date = datetime.datetime.utcnow()
    start_date = current_date - datetime.timedelta(days=7)
    while start_date < current_date:
        f = '3B-HHR-E.MS.MRG.3IMERG.{}-S120000-E175959.1050.V03E.1day.tif'
        file = f.format(
            current_date.strftime('%Y%m%d'))
        file_list.append(file)
        current_date = current_date - datetime.timedelta(days=1)
    return file_list


def mock_none(self, *args):
    """
    For mocking various FTP methods that should return nothing for tests.
    """
    return None


class NasaGpmTest(TestCase):
    """
    Tests the dataqs.nasa_gpm module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = GPMProcessor()

    def tearDown(self):
        self.processor.cleanup()

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary)
    @patch('ftplib.FTP.nlst', mock_nlst)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_download(self, mock_ftp):
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
        f = '3B-HHR-E.MS.MRG.3IMERG.20151027-S133000-E135959.0810.V03E.1day.tif'
        title = self.processor.parse_name(f)[0]
        self.assertTrue('NASA Global Precipitation Estimate (1day) - 2015-10-27'
                        in title)

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary)
    @patch('ftplib.FTP.nlst', mock_nlst)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_convert_image(self, mock_ftp):
        """
        Converted image should be create in temp directory
        :return:
        """
        dl_tif = self.processor.download()[0]
        convert_tif = self.processor.convert(dl_tif)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, convert_tif)))

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary)
    @patch('ftplib.FTP.nlst', mock_nlst)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_cleanup(self, mock_ftp):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        dl_tif = self.processor.download()[0]
        self.processor.convert(dl_tif)
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
