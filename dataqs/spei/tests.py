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
import os
from django.test import TestCase
from dataqs.spei.spei import SPEIProcessor
import httpretty

script_dir = os.path.dirname(os.path.realpath(__file__))


def get_mock_image():
    """
    Return a canned response with HTML for Boston
    """
    zf = zipfile.ZipFile(os.path.join(script_dir,
                                      'resources/test_spei.zip'))

    return zf.read('test_spei.tif')


class SpieTest(TestCase):
    """
    Tests the dataqs.spie module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = SPEIProcessor()
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        imgurl = "{}spei03.nc".format(self.processor.base_url)
        httpretty.register_uri(httpretty.GET, imgurl,
                               body=get_mock_image())
        imgfile = self.processor.download(imgurl, 'spei03.tif')
        self.assertTrue(os.path.exists(os.path.join(
            self.processor.tmp_dir, imgfile)))

    def test_cleanup(self):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        imgurl = "{}spei03.nc".format(self.processor.base_url)
        httpretty.register_uri(httpretty.GET, imgurl,
                               body=get_mock_image())
        self.processor.download(imgurl, 'spei03.tif')
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
