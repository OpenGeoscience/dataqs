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

from __future__ import absolute_import
import logging
import os
import re
import shutil
from datetime import date
from ftplib import FTP

from dateutil.relativedelta import relativedelta
from dataqs.processor_base import GeoDataMosaicProcessor, GS_DATA_DIR, \
    GS_TMP_DIR
from dataqs.helpers import get_band_count, gdal_translate, \
    nc_convert, style_exists, cdo_fixlng

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class UoDAirTempPrecipProcessor(GeoDataMosaicProcessor):
    """
    Processor for Land-Ocean Temperature Index, ERSSTv4, 1200km smoothing
    from the NASA Goddard Institute for Space Studies' Surface Temperature
    Analysis (GISTEMP).
    More info at http://data.giss.nasa.gov/gistemp/
    """
    prefix = "uod_"
    base_url = "ftp.cdc.noaa.gov"

    layers = {
        'air.mon.mean.v401.nc': {
            'title': 'U. Delaware Monthly Mean Air Temperature 1901 - 2015',
            'name': 'uod_air_mean_401'
        },
        'precip.mon.total.v401.nc': {
            'title': 'U. Delaware Monthly Total Precipitation 1901 - 2015',
            'name': 'uod_precip_total_401'
        }

    }
    abstract = """Cort Willmott & Kenji Matsuura of the University of Delaware
    have put data together from a large number of stations, both from the GHCN2
    (Global Historical Climate Network) and, more extensively, from the archive
    of Legates & Willmott. More details can be found here for temperature and
    here for precipitation. The result is a monthly climatology of precipitation
     and air temperature, both at the surface, and a time series, spanning 1900
    to 2010, of monthly mean surface air temperatures, and monthly total
    precipitation. It is land-only in coverage, and complements the ICOADS
    (International Comprehensive Ocean-Atmosphere Data Set) data set well. For a
     complete description of the data as given by the providers, related
    datasets and references to relevant papers please see their web pages at the
     University of Delaware..

    Source: http://www.esrl.noaa.gov/psd/data/gridded/data.UDel_AirT_Precip.html

    The displayed image is based on the most current month.

Citations:
    - Willmott, C. J. and K. Matsuura (2001) Terrestrial Air Temperature and
    Precipitation: Monthly and Annual Time Series (1950 - 1999),
    http://climate.geog.udel.edu/~climate/html_pages/README.ghcn_ts2.html.
    - UDel_AirT_Precip data provided by the NOAA/OAR/ESRL PSD, Boulder,
    Colorado, USA, from their Web site at http://www.esrl.noaa.gov/psd/
 """

    def download(self, tmp_dir=GS_TMP_DIR):
        """
        Retrieve NetCDF files via FTP
        :param tmp_dir: Temp directory to store files
        :return: list of saved output files
        """
        ftp = FTP(self.base_url)
        ftp.login('anonymous', 'anonymous')
        ftp.cwd('/Datasets/udel.airt.precip/')
        outfiles = []
        for file in self.layers.keys():
            outfile = os.path.join(tmp_dir, '{}{}'.format(self.prefix, file))
            with open(outfile, 'wb') as output:
                ftp.retrbinary('RETR %s' % file, output.write)
            outfiles.append(outfile)
        return outfiles

    def convert(self, nc_file):
        nc_transform = nc_convert(nc_file)
        cdo_transform = cdo_fixlng(nc_transform)
        return cdo_transform

    def extract_band(self, tif, band, outname):
        outfile = os.path.join(self.tmp_dir, outname)
        gdal_translate(tif, outfile, bands=[band],
                       projection='EPSG:4326',
                       options=['TILED=YES', 'COMPRESS=LZW'])
        return outfile

    def get_date(self, months):
        start_month = date(1901, 1, 1)
        return start_month + relativedelta(months=months - 1)

    def run(self):
        """
        Retrieve and process the latest NetCDF file.
        """
        cdf_files = self.download()
        for cdf in cdf_files:
            cdf_file = self.convert(cdf)
            bands = get_band_count(cdf_file)
            key = os.path.basename(cdf).lstrip(self.prefix)
            print(key)
            layer_name = self.layers[key]['name']
            img_list = self.get_mosaic_filenames(layer_name)
            for band in range(1, bands + 1):
                band_date = re.sub('[\-\.]+', '',
                                   self.get_date(band).isoformat())
                img_name = '{}_{}T000000000Z.tif'.format(layer_name, band_date)
                if img_name not in img_list:
                    band_tif = self.extract_band(cdf_file, band, img_name)
                    dst_file = self.data_dir.format(gsd=GS_DATA_DIR,
                                                    ws=self.workspace,
                                                    layer=layer_name,
                                                    file=img_name)
                    dst_dir = os.path.dirname(dst_file)
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                    if dst_file.endswith('.tif'):
                        shutil.move(os.path.join(self.tmp_dir, band_tif),
                                    dst_file)
                        self.post_geoserver(dst_file, layer_name)

            if not style_exists(layer_name):
                with open(os.path.join(script_dir, 'resources/{}.sld'.format(
                        layer_name))) as sld:
                    print(layer_name,
                          os.path.join(script_dir,
                                       'resources/{}.sld'.format(layer_name)))
                    self.set_default_style(layer_name, layer_name, sld.read())
            self.update_geonode(layer_name,
                                title=self.layers[key]['title'],
                                description=self.abstract,
                                store=layer_name,
                                bounds=('-180.0', '180.0', '-90.0', '90.0',
                                        'EPSG:4326'))
            self.truncate_gs_cache(layer_name)
        self.cleanup()


if __name__ == '__main__':
    processor = UoDAirTempPrecipProcessor()
    processor.run()
