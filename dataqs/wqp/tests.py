import glob
import os
import datetime
from django.test import TestCase
from dataqs.wqp.wqp import WaterQualityPortalProcessor
import unicodecsv as csv


class WaterQualityTest(TestCase):
    """
    Tests the dataqs.wqp module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = WaterQualityPortalProcessor(days=7)

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        files = self.processor.download('pH')
        self.assertTrue('Result' in files)
        self.assertTrue('Station' in files)

        station_file = os.path.join(self.processor.tmp_dir, files['Station'])
        result_file = os.path.join(self.processor.tmp_dir, files['Result'])
        self.assertTrue(os.path.exists(station_file), "Station file not found")
        self.assertTrue(os.path.exists(result_file), "Result file not found")

        stations = []
        with open(station_file) as inputfile:
            reader = csv.DictReader(inputfile)
            for row in reader:
                stations.append(row['MonitoringLocationIdentifier'])

        with open(result_file) as inputfile:
            reader = csv.DictReader(inputfile)
            for row in reader:
                self.assertEquals(row['CharacteristicName'], 'pH')
                self.assertTrue(row['MonitoringLocationIdentifier'] in stations)

    def test_safe_name(self):
        self.assertEquals('inorganicnitrogennitrateandnitrite',
                          self.processor.safe_name(
                              'Inorganic nitrogen (nitrate and nitrite)'))
        self.assertEquals('temperaturewater',
                          self.processor.safe_name(
                              'Temperature, water'))

    def test_cleanup(self):
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
