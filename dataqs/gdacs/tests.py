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

import os
import datetime
from django.test import TestCase
from dataqs.gdacs.gdacs import GDACSProcessor
import httpretty
from xml.etree import ElementTree as et

script_dir = os.path.dirname(os.path.realpath(__file__))


class GdacsTest(TestCase):
    """
    Tests the dataqs.gdacs module.  Since each processor is highly
    dependent on a running GeoNode instance for most functions, only
    independent functions are tested here.
    """

    def setUp(self):
        today = datetime.datetime.utcnow()
        self.edate = today.strftime("%Y-%m-%d")
        self.sdate = (today - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        self.processor = GDACSProcessor(edate=self.edate, sdate=self.sdate)
        httpretty.enable()

    def tearDown(self):
        httpretty.disable()
        self.processor.cleanup()

    def test_download(self):
        """
        Verify that files are downloaded.
        """
        with open(os.path.join(script_dir, 'resources/test_gdacs.rss')) as inf:
            response = inf.read()
        httpretty.register_uri(httpretty.GET, self.processor.base_url,
                               body=response)
        rssfile = self.processor.download(self.processor.base_url.format(
            self.processor.params['sdate'], self.processor.params['edate']),
            filename=self.processor.prefix + ".rss")
        rsspath = os.path.join(
            self.processor.tmp_dir, rssfile)
        self.assertTrue(os.path.exists(rsspath))
        with open(rsspath) as rssin:
            rss_tree = et.fromstring(rssin.read())
            self.assertEquals(len(rss_tree.findall('channel/item')), 65)

    def test_cleanup(self):
        """
        Temporary files should be gone after cleanup
        :return:
        """
        with open(os.path.join(script_dir, 'resources/test_gdacs.rss')) as inf:
            response = inf.read()
        httpretty.register_uri(httpretty.GET, self.processor.base_url,
                               body=response)
        rssfile = self.processor.download(self.processor.base_url.format(
            self.processor.params['sdate'], self.processor.params['edate']),
            filename=self.processor.prefix + ".rss")
        rsspath = os.path.join(
            self.processor.tmp_dir, rssfile)
        self.assertTrue(os.path.exists(rsspath))
        self.processor.cleanup()
        self.assertFalse(os.path.exists(rsspath))
