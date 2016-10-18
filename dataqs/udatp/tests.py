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
import unittest
from datetime import date
from django.test import TestCase
from dataqs.udatp.udatp import UoDAirTempPrecipProcessor
from mock import patch

script_dir = os.path.dirname(os.path.realpath(__file__))


def mock_retrbinary_nc(self, name, writer):
    """
    Mocks the ftplib.FTP.retrbinary method, writes test image to disk.
    """
    with open(os.path.join(script_dir, 'resources/uodtest.nc'), 'rb') as inf:
        writer(inf.read())
    return None


def mock_retrbinary_tif(self, name, writer):
    """
    Mocks the ftplib.FTP.retrbinary method, writes test image to disk.
    """
    with open(os.path.join(script_dir, 'resources/uodtest.tif'), 'rb') as inf:
        writer(inf.read())
    return None


def mock_none(self, *args):
    """
    For mocking various FTP methods that should return nothing for tests.
    """
    return None


class UoDAirTempPrecipTest(TestCase):
    """
    Tests the dataqs.gistemp module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        self.processor = UoDAirTempPrecipProcessor()

    def tearDown(self):
        self.processor.cleanup()

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary_nc)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_download(self, ftp_mock):
        """
        Verify that a file is downloaded
        """
        cdf_files = self.processor.download()
        for cdf in cdf_files:
            self.assertTrue(os.path.exists(cdf))

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary_nc)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_cleanup(self, ftp_mock):
        self.processor.download()
        self.assertNotEqual([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))
        self.processor.cleanup()
        self.assertEquals([], glob.glob(os.path.join(
            self.processor.tmp_dir, self.processor.prefix + '*')))

    def test_date(self):
        last_date = self.processor.get_date(1380)
        self.assertEquals(last_date, date(2015, 12, 1))

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary_nc)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_convert(self, ftp_mock):
        cdf_files = self.processor.download()
        for cdf in cdf_files:
            try:
                self.processor.convert(cdf)
                self.assertNotEqual([], glob.glob(cdf.replace(
                    '.nc', '.classic.lng.nc')))
            except OSError:
                # cdo and/or netcdf not installed
                raise unittest.SkipTest()

    @patch('ftplib.FTP', autospec=True)
    @patch('ftplib.FTP.retrbinary', mock_retrbinary_tif)
    @patch('ftplib.FTP.connect', mock_none)
    @patch('ftplib.FTP.login', mock_none)
    @patch('ftplib.FTP.cwd', mock_none)
    def test_extract_band(self, ftp_mock):
        cdf = self.processor.download()[0]
        tif = cdf.replace('.nc', '.tif')
        self.processor.extract_band(cdf, 1, tif)
        self.assertTrue(os.path.isfile(tif))
