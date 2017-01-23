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
from dateutil.relativedelta import relativedelta
from dataqs.processor_base import GeoDataMosaicProcessor, GS_DATA_DIR
from dataqs.helpers import get_band_count, gdal_translate, \
    nc_convert, style_exists, cdo_fixlng, gunzip

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class GISTEMPProcessor(GeoDataMosaicProcessor):
    """
    Processor for Land-Ocean Temperature Index, ERSSTv4, 1200km smoothing
    from the NASA Goddard Institute for Space Studies' Surface Temperature
    Analysis (GISTEMP).
    More info at http://data.giss.nasa.gov/gistemp/
    """
    prefix = "gistemp"
    base_url = "http://data.giss.nasa.gov/pub/gistemp/gistemp1200_ERSSTv4.nc.gz"
    layer_name = 'gistemp1200_ERSSTv4'
    title = 'Global Monthly Air Temperature Anomalies, 1880/01/01 - {}'
    abstract = """The GISTEMP analysis recalculates consistent temperature
anomaly series from 1880 to the present for a regularly spaced array of virtual
stations covering the whole globe. Those data are used to investigate regional
and global patterns and trends.  Graphs and tables are updated around the
middle of every month using current data files from NOAA GHCN v3 (meteorological
 stations), ERSST v4 (ocean areas), and SCAR (Antarctic stations).

 The displayed image is based on the most current month.

Citations:
    - GISTEMP Team, 2016: GISS Surface Temperature Analysis (GISTEMP).
      NASA Goddard Institute for Space Studies.  Dataset accessed monthly
      since 8/2016 at http://data.giss.nasa.gov/gistemp/.
    - Hansen, J., R. Ruedy, M. Sato, and K. Lo, 2010: Global surface
      temperature change, Rev. Geophys., 48, RG4004, doi:10.1029/2010RG000345.

 """

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
        start_month = date(1880, 1, 1)
        return start_month + relativedelta(months=months-1)

    def get_title(self, months):
        end_month = self.get_date(months)
        return self.title.format(end_month.strftime('%Y/%m/%d'))

    def run(self):
        """
        Retrieve and process the latest NetCDF file.
        """
        gzfile = self.download(
            self.base_url, '{}.nc.gz'.format(self.layer_name))
        ncfile = gunzip(os.path.join(self.tmp_dir, gzfile))
        cdf_file = self.convert(ncfile)
        bands = get_band_count(cdf_file)
        img_list = self.get_mosaic_filenames(self.layer_name)
        for band in range(1, bands+1):
            band_date = re.sub('[\-\.]+', '', self.get_date(band).isoformat())
            img_name = '{}_{}T000000000Z.tif'.format(self.layer_name, band_date)
            if img_name not in img_list:
                band_tif = self.extract_band(cdf_file, band, img_name)
                dst_file = self.data_dir.format(gsd=GS_DATA_DIR,
                                                ws=self.workspace,
                                                layer=self.layer_name,
                                                file=img_name)
                dst_dir = os.path.dirname(dst_file)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                if dst_file.endswith('.tif'):
                    shutil.move(os.path.join(self.tmp_dir, band_tif), dst_file)
                    self.post_geoserver(dst_file, self.layer_name)

        if not style_exists(self.layer_name):
            with open(os.path.join(script_dir,
                                   'resources/gistemp.sld')) as sld:
                self.set_default_style(self.layer_name, self.layer_name,
                                       sld.read().format(latest_band=bands))
        self.update_geonode(
            self.layer_name, title=self.get_title(bands),
            description=self.abstract,
            store=self.layer_name,
            bounds=('-180.0', '180.0', '-90.0', '90.0',
                    'EPSG:4326'),
            extra_keywords=['category:Climatology Meteorology'])
        self.truncate_gs_cache(self.layer_name)
        self.cleanup()


if __name__ == '__main__':
    processor = GISTEMPProcessor()
    processor.run()
