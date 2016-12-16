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
import os
import datetime
from urlparse import urlparse, parse_qs
from dataqs.ndvi16modis.ndvi16modis import NDVI16MODISProcessor
from django.test import TestCase
import httpretty

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_test_image():
    """
    Return a canned response with HTML for Boston
    """
    with open(os.path.join(script_dir, 'resources/test_ndvi.tif'), 'rb') as inf:
        return inf.read()


def get_test_page():
    """
    Return a canned response with HTML for Boston
    """
    with open(os.path.join(script_dir, 'resources/test_ndvi.html'), 'r') as inf:
        return inf.read()


class NDVI16MODISProcessorTest(TestCase):
    """
    Tests the dataqs.ndvi16modis module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = NDVI16MODISProcessor()
        self.processor.tmp_dir = os.path.join(script_dir, "resources")
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_get_image_url_date(self):
        """
        Verify that the expected image url and date interval are returned
        :return:
        """
        test_date = '2016-12-13'
        test_url = self.processor.base_url.format(
            ds=self.processor.dataset, dt=test_date)
        httpretty.register_uri(httpretty.GET, test_url,
                               body=get_test_page(),
                               content_type="text/html")
        url, dt = self.processor.get_image_url_date(test_date)
        url_parts = urlparse(url)
        qs = parse_qs(url_parts.query)
        self.assertEquals(url_parts.netloc, 'neo.sci.gsfc.nasa.gov')
        self.assertTrue('1710813' in qs['si'])
        self.assertTrue('FLOAT.TIFF' in qs['format'])

    def test_parse_date(self):
        """
        Layer title should contain date of image
        :return:
        """
        test_interval = "March 1 - 17, 2010"
        interval_date = self.processor.parse_date(test_interval)
        self.assertEquals(datetime.datetime(2010, 3, 17), interval_date)

        test_interval = "March 18 - April 1, 2010"
        interval_date = self.processor.parse_date(test_interval)
        self.assertEquals(datetime.datetime(2010, 4, 1), interval_date)

    def test_convert_image(self):
        """
        Verifies that the original image is translated into a new one with the
        expected name and location.
        :return:
        """
        test_date = datetime.datetime(2010, 3, 17)
        out_img = self.processor.convert('test_ndvi.tif', test_date)
        expected = 'ndvimodis16_20100317T000000000Z.tif'
        self.assertEquals(out_img, expected)
        self.assertTrue(os.path.exists(
            os.path.join(self.processor.tmp_dir, expected)))

    def test_cleanup(self):
        """
        Verifies that no images are left over after cleanup
        :return:
        """
        test_date = datetime.date(2010, 3, 17)
        self.processor.convert('test_ndvi.tif', test_date)
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
