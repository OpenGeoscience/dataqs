import glob
import json
import httpretty
import os
from django.test import TestCase
from dataqs.whisp.whisp import WhispProcessor
import mock

script_dir = os.path.dirname(os.path.realpath(__file__))


def test_data():
    with open(os.path.join(script_dir, 'resources/test_whisp.html')) as html:
        return html.read()


def mock_insert_row(self, data):
    with open(os.path.join(
            self.tmp_dir, '().json'.format(self.prefix)), 'w') as testfile:
        json.dump(data, testfile)


class WhispTest(TestCase):
    """
    Tests the dataqs.whisp module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = WhispProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    @mock.patch('dataqs.whisp.whisp.WhispProcessor.insert_row', mock_insert_row)
    def test_scrape(self):
        """
        Verify that the correct records can be read from html
        :return:
        """
        httpretty.register_uri(
            httpretty.GET,
            self.processor.base_url,
            body=test_data(),
            content_type='text/html')
        self.processor.scrape()
        testfile = os.path.join(
            self.processor.tmp_dir, '().json'.format(self.processor.prefix))
        self.assertTrue(os.path.exists(testfile))
        with open(testfile) as test:
            test_json = json.load(test)
            self.assertTrue(test_json['eventtype'])
            self.assertTrue(test_json['the_geom'])
        self.processor.cleanup()

    @mock.patch('dataqs.whisp.whisp.WhispProcessor.insert_row', mock_insert_row)
    def test_archive_import(self):
        """
        Verify that the correct records can be read from archive
        :return:
        """
        self.processor.import_archive()
        testfile = os.path.join(
            self.processor.tmp_dir, '().json'.format(self.processor.prefix))
        self.assertTrue(os.path.exists(testfile))
        with open(testfile) as test:
            test_json = json.load(test)
            self.assertTrue(test_json['eventtype'])
            self.assertTrue(test_json['the_geom'])
        self.processor.cleanup()

    @mock.patch('dataqs.whisp.whisp.WhispProcessor.insert_row', mock_insert_row)
    def test_cleanup(self):
        httpretty.register_uri(
            httpretty.GET,
            self.processor.base_url,
            body=test_data(),
            content_type='text/html')
        self.processor.scrape()
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
