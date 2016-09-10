#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc. and Epidemico Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import glob
import zipfile
import httpretty
import os
from django.test import TestCase
from dataqs.wqp.wqp import WaterQualityPortalProcessor
import unicodecsv as csv

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_mock_response(filename):
    """
    Return a canned response with HTML for Boston
    """
    zf = zipfile.ZipFile(os.path.join(script_dir,
                                      'resources/test_wqp_ph.zip'))

    return zf.read(filename)


class WaterQualityTest(TestCase):
    """
    Tests the dataqs.wqp module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = WaterQualityPortalProcessor(days=7)
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        for qtype in ('Result', 'Station'):
            url = ('http://www.waterqualitydata.us/{}/search?'.format(qtype) +
                   'countrycode=US&startDateLo=12-27-2015' +
                   '&startDateHi=01-26-2016' +
                   '&characteristicName=pH')
            httpretty.register_uri(httpretty.GET, url,
                                   body=get_mock_response(
                                       'test_wqp_ph_{}.csv'.format(qtype)))

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
        """
        Verify that the correct safe name is returned for indicators
        """
        self.assertEquals('inorganicnitrogennitrateandnitrite',
                          self.processor.safe_name(
                              'Inorganic nitrogen (nitrate and nitrite)'))
        self.assertEquals('temperaturewater',
                          self.processor.safe_name(
                              'Temperature, water'))

    def test_cleanup(self):
        """
        Verify that no stray files exist after cleanup
        """
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
