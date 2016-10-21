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
from datetime import date

import gdal
import httpretty
from dataqs.hadghcnd.hadghcnd import HadGHCNDProcessor
from django.test import TestCase

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_mock_image():
    """
    Return a canned test image (1 band of original NetCDF raster)
    """
    nc = os.path.join(script_dir,
                      'resources/HadGHCND_TXTN_anoms_1950-1960_15052015.nc')
    with open(nc, 'rb') as ncfile:
        return ncfile.read()


class HadGHCNDTest(TestCase):
    """
    Tests the dataqs.hadghcnd module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = HadGHCNDProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that a file is downloaded
        """
        httpretty.register_uri(httpretty.GET,
                               self.processor.base_url,
                               body=get_mock_image())
        layer = self.processor.layers.keys()[0]
        imgfile = self.processor.download(
            self.processor.base_url, layer)
        self.assertTrue(os.path.exists(
            os.path.join(self.processor.tmp_dir, imgfile)))

    def test_extract_band(self):
        httpretty.register_uri(httpretty.GET,
                               self.processor.base_url,
                               body=get_mock_image())
        layer = self.processor.layers.keys()[0]
        imgfile = self.processor.download(
            self.processor.base_url, layer.rstrip('.tgz'))
        ncds_gdal_name = 'NETCDF:{}:tmin'.format(
            os.path.join(self.processor.tmp_dir, imgfile))
        bandout = os.path.join(self.processor.tmp_dir,
                               '{}test'.format(self.processor.prefix))
        self.processor.extract_band(ncds_gdal_name, 1, bandout)
        self.assertTrue(os.path.exists(os.path.join(bandout)))
        img = gdal.Open(bandout)
        try:
            self.assertEquals(1, img.RasterCount)
        finally:
            del img

    def test_date(self):
        self.assertEquals(self.processor.get_date(712224), date(1950, 1, 1))
        self.assertEquals(self.processor.get_date(735964), date(2014, 12, 31))

    def test_cleanup(self):
        httpretty.register_uri(httpretty.GET,
                               self.processor.base_url,
                               body=get_mock_image())
        layer = self.processor.layers.keys()[0]
        self.processor.download(self.processor.base_url, layer)
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
