import glob
import zipfile
import os
import datetime
from django.test import TestCase
from dataqs.airnow.airnow import AirNowGRIB2HourlyProcessor
from mock import patch

script_dir = os.path.dirname(os.path.realpath(__file__))


def mock_retrbinary(self, name, writer):
    """
    Mocks the ftplib.FTP.retrbinary method, writes test image to disk.
    """
    zf = zipfile.ZipFile(os.path.join(script_dir, 'resources/test_airnow.zip'))
    writer(zf.read('test_airnow.grib2'))
    return None


def mock_nlst(self, *args):
    """
    Mocks the ftplib.FTP.nlst method, returns a list of files based on date.
    """
    file_list = []
    current_date = datetime.datetime.utcnow()
    start_date = current_date - datetime.timedelta(days=7)
    while start_date < current_date:
        file_base = '2US-{}12'.format(
            current_date.strftime('%y%m%d'))
        for f in ('', '_pm25', '_combined'):
            file_list.append('{}{}.grib2'.format(file_base, f))
        current_date = current_date - datetime.timedelta(days=1)
    return file_list


def mock_none(self, *args):
    """
    For mocking various FTP methods that should return nothing for tests.
    """
    return None


class AirNowTest(TestCase):
    """
    Tests the dataqs.airnow module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = AirNowGRIB2HourlyProcessor()

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
        files = self.processor.download()
        today = datetime.datetime.utcnow().strftime('airnow_2US-%y%m%d')
        self.testfile = files[0]
        # Should be 3 files for 1 day
        self.assertEquals(3, len(files))
        # Should be files for today
        for dfile in files:
            self.assertTrue(dfile.startswith(today))

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary)
    @patch('ftplib.FTP.nlst', mock_nlst)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_download_multiple_days(self, mock_ftp):
        """
        Verify that files are downloaded for multiple days.
        """
        today = datetime.datetime.today()
        dates = [(today - datetime.timedelta(days=x)).strftime(
            '%y%m%d') for x in range(2)]
        ftypes = ('', '_pm25', '_combined')
        files = self.processor.download(days=3)
        # Should be 3 files per day == 9 files
        self.assertEquals(9, len(files))
        for date in dates:
            for ftype in ftypes:
                self.assertIn(
                    'airnow_2US-{}12{}.grib2'.format(date, ftype), files)

    def test_parse_name(self):
        """
        Verify that the correct layer titles & names are used.
        """
        title, name, imgtime = self.processor.parse_name('US-15100215.grib2')
        self.assertEquals(
            'AirNow Hourly Air Quality Index (Ozone) - 2015-10-02 15:00 UTC',
            title)
        self.assertEquals('airnow_aqi_ozone', name)
        self.assertEquals(datetime.datetime(2015, 10, 2, 15, 0), imgtime)

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary)
    @patch('ftplib.FTP.nlst', mock_nlst)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_convert_image(self, mock_ftp):
        """
        Verify that a TIF file is created from a test GRIB file
        """
        files = self.processor.download()
        title, name, imgtime = self.processor.parse_name(files[0])
        tif_file = self.processor.convert(files[0], imgtime, name)
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, tif_file)))

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary)
    @patch('ftplib.FTP.nlst', mock_nlst)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_cleanup(self, mock_ftp):
        """
        Verify that no associated files remain on disk after cleanup
        :return:
        """
        self.processor.download()
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
