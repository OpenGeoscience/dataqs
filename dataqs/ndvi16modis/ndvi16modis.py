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
import logging
import os
from datetime import datetime
import re
import requests
import shutil
from bs4 import BeautifulSoup as bs
from dataqs.helpers import style_exists, gdal_translate
from dataqs.processor_base import GeoDataMosaicProcessor, GS_DATA_DIR

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class NDVI16MODISProcessor(GeoDataMosaicProcessor):
    """
    Processor for 16-Day NDVI images from the TERRRA/MODIS satellite.
    """
    dataset = "MOD13A2_E_NDVI"
    layer_title = "NDVI 16-Day Mosaic: {dt}"
    base_url = "http://neo.sci.gsfc.nasa.gov/view.php?datasetId={ds}&date={dt}"
    prefix = 'ndvimodis16'
    description = u"""16-Day Normalized Difference Vegetation Index (NDVI) made
from data collected by the Moderate Resolution Imaging Spectroradiometer
(MODIS) aboard NASA's Terra satellite. These NDVI maps are robust, empirical
measures of vegetation activity at the land surface. They are designed to
enhance the vegetation signal from measured spectral responses by combining two
(or more) different wavebands, often in the red (0.6-0.7 mm) and near-infrared
wavelengths (0.7-1.1 mm). Reflected red energy decreases with plant development
due to chlorophyll absorption within actively photosynthetic leaves. Reflected
near-infrared energy, on the other hand, will increase with plant development
through scattering processes (reflection and transmission) in healthy, turgid
leaves. Unfortunately - because the amount of red and near-infrared radiation
reflected from a plant canopy and reaching a satellite sensor varies with solar
irradiance, atmospheric conditions, canopy background, canopy structure, and
canopy composition - one cannot use a simple measure of reflected energy to
quantify plant biophysical parameters nor monitor vegetation on a global,
operational basis. This problem is made more difficult due to the intricate
radiant transfer processes at both the leaf level (i.e., cell constituents,
leaf morphology) and canopy level (i.e., leaf elements, orientation, non-
photosynthetic vegetation, and background)."""

    def get_image_url_date(self, date_str):
        """
        Parse the web page to find appropriate download link and date range
        :param date_str: date string to retrieve 16-day interval for (Y-m-d).
        :return: URL of image download, date interval as string
        """
        soup = bs(requests.get(
            self.base_url.format(ds=self.dataset, dt=date_str)).content)
        latest_date = soup.find(id='download-date').text
        latest_url = soup.find(
            'a', text='3600 x 1800').attrs["href"].replace("JPEG", "FLOAT.TIFF")
        return latest_url, latest_date

    def parse_date(self, datestr):
        """
        Given a date interval like "November 1 - 17, 2016" return a date
        object for the last day in that interval.
        :param datestr: date interval as string
        :return: date object
        """
        parts = re.match(r"(\w+)\s+\d+\s+\-\s+(\d+),\s(\d{4})", datestr)
        return datetime.strptime("%s %s %s" % parts.group(1, 2, 3), "%B %d %Y")

    def convert(self, tif_file, dt):
        """
        Set NoData value and projection of input TIF, saving as a new TIF with
        timestamp in the name.
        :param tif_file: Filepath of input TIF
        :param dt: date object
        :return: Filepath of new TIF image
        """
        tif_out = "{prefix}_{date}.tif".format(
            prefix=self.prefix,
            date=self.mosaic_date_format(dt)
        )
        # Use gdal_translate to embed projection info
        gdal_translate(os.path.join(self.tmp_dir, tif_file),
                       os.path.join(self.tmp_dir, tif_out),
                       nodata=99999.000, projection="EPSG:4326")
        return tif_out

    def run(self, datestr=None):
        """
        Run the processor
        :param datestr: Date to retrieve interval for
        """
        if not datestr:
            datestr = datetime.now().strftime('%Y-%m-%d')
        img_url, interval = self.get_image_url_date(datestr)
        img_date = self.parse_date(interval)
        tif = self.download(img_url,
                            '{}{}.tif'.format(self.prefix, datestr))
        converted_tif = self.convert(tif, img_date)
        dst_file = self.data_dir.format(gsd=GS_DATA_DIR, ws=self.workspace,
                                        layer=self.prefix,
                                        file=converted_tif)
        dst_dir = os.path.dirname(dst_file)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        if dst_file.endswith('.tif'):
            shutil.move(os.path.join(self.tmp_dir, converted_tif), dst_file)
            self.post_geoserver(dst_file, self.prefix)

        self.drop_old_hourly_images(img_date, self.prefix)
        self.drop_old_daily_images(img_date, self.prefix)
        if not style_exists(self.prefix):
            with open(os.path.join(script_dir, 'resources/ndvi.sld')) as sld:
                self.set_default_style(self.prefix,
                                       self.prefix, sld.read())
        self.update_geonode(self.prefix,
                            title=self.layer_title.format(dt=interval),
                            description=self.description,
                            store=self.prefix,
                            bounds=('-180.0', '180.0', '-90.0', '90.0',
                                    'EPSG:4326'))
        self.truncate_gs_cache(self.prefix)
        self.cleanup()

    def cleanup(self):
        """
        Remove any files in the temp directory matching
        the processor class prefix or layer name
        """
        filelist = glob.glob("{}*.*".format(
            os.path.join(self.tmp_dir, self.prefix)))
        for f in filelist:
            os.remove(f)
        super(NDVI16MODISProcessor, self).cleanup()

if __name__ == '__main__':
    processor = NDVI16MODISProcessor()
    processor.run()

