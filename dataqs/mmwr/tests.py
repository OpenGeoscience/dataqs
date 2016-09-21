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
import json
import httpretty
import os
import datetime
from django.test import TestCase
from dataqs.mmwr.mmwr import MortalityProcessor
import unicodecsv as csv

script_dir = os.path.dirname(os.path.realpath(__file__))


def test_data():
    with open(os.path.join(script_dir, 'resources/test_mmwr.txt')) as csv:
        return csv.read()


class MMWRTest(TestCase):
    """
    Tests the dataqs.mmwr module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = MortalityProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that a file is downloaded
        """
        report_date = datetime.date(2016, 1, 15)
        httpretty.register_uri(
            httpretty.GET,
            self.processor.base_url.format(week=2, year=2016),
            body=test_data())
        self.processor.generate_csv(report_date)
        output = os.path.join(
            self.processor.tmp_dir, '{}.txt'.format(self.processor.prefix))
        self.assertTrue(os.path.exists(output))
        with open(output) as ofile:
            self.assertEquals(ofile.read(), test_data())

    def test_generate_csv(self):
        """
        Verify that a correct csv file is generated
        :return:
        """
        report_date = datetime.date(2016, 1, 15)
        httpretty.register_uri(
            httpretty.GET,
            self.processor.base_url.format(week=2, year=2016),
            body=test_data())
        self.processor.generate_csv(report_date)
        output = os.path.join(
            self.processor.tmp_dir, '{}.csv'.format(self.processor.prefix))
        self.assertTrue(os.path.exists(output))
        with open(output) as ofile:
            reader = csv.reader(ofile)
            headers = reader.next()
            with open(os.path.join(script_dir, 'resources/mmwr.json')) as locs:
                locations = json.load(locs)
            self.assertEquals(
                headers, ['place', 'lng', 'lat', 'all', 'a65',
                          'a45_64', 'a25_44', 'a01-24', 'a01', 'flu',
                          'report_date'])
            for row in reader:
                self.assertIn(row[0], locations)
                self.assertEquals(float(row[1]), locations[row[0]][1])
                self.assertEquals(float(row[2]), locations[row[0]][0])

    def test_cleanup(self):
        report_date = datetime.date(2016, 1, 15)
        httpretty.register_uri(
            httpretty.GET,
            self.processor.base_url.format(week=2, year=2016),
            body=test_data())
        self.processor.generate_csv(report_date)
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
