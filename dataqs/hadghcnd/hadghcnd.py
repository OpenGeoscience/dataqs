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
from time import sleep
import gdal
from dateutil.relativedelta import relativedelta
from dataqs.processor_base import GeoDataMosaicProcessor, GS_DATA_DIR, \
    GS_TMP_DIR, RSYNC_WAIT_TIME
from dataqs.helpers import gdal_translate, style_exists,  create_band_vrt, untar

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class HadGHCNDProcessor(GeoDataMosaicProcessor):
    """
    Hadley Centre gridded daily temperature dataset based upon near-surface
    maximum (TX) and minimum (TN) temperature observations.
    It is designed primarily for the analysis of climate extremes and also for
    climate model evaluation. It spans the years 1950 to present and is
    available on a 2.5° latitude by 3.75° longitude grid. This dataset has
    been developed in collaboration with the United States National Centers for
    Environmental Information (NCEI), formerly the National Climatic Data Center
    (NCDC).
    More info at http://www.metoffice.gov.uk/hadobs/hadghcnd/index.html
    """
    prefix = "HadGHCND"
    tmp_dir = os.path.join(GS_TMP_DIR, prefix)
    base_url = "http://www.metoffice.gov.uk/hadobs/hadghcnd/data/"

    layers = {
        'HadGHCND_TXTN_anoms_1950-2014_15052015.nc.tgz': {
            'title': 'HadGHCND Temperature Anomalies - {measure}, 1950-2014',
            'name': '{prefix}_anomalies_{measure}'
        },
        'HadGHCND_TXTN_acts_1950-2014_15102015.nc.tgz': {
            'title': 'HadGHCND Actual Temperatures - {measure}, 1950-2014',
            'name': '{prefix}_temperatures_{measure}'
        }

    }
    abstract = (
        u"HadGHCND is a gridded daily temperature dataset based upon near-"
        u"surface maximum (TX) and minimum (TN) temperature observations. It is"
        u" designed primarily for the analysis of climate extremes and also for"
        u" climate model evaluation. It spans the years 1950 to present and is "
        u"available on a 2.5° latitude by 3.75° longitude grid. This dataset "
        u"has been developed in collaboration with the United States National "
        u"Centers for Environmental Information (NCEI), formerly the National "
        u"Climatic Data Center (NCDC).\n\nHadGHCND has been created using daily"
        u" station observations in NCEI's GHCN (Global Historical Climatology "
        u"Network)-Daily database. This consists of over 27,000 stations with "
        u"temperature observations, though many of these have quite short "
        u"records, or gaps in the record. Quality control has been carried out "
        u"to indicate potentially spurious values. We have filtered down these "
        u"stations to obtain those for which we can adequately calculate a 1961"
        u"-90 daily climatology. The dataset represents anomalies from the 1961"
        u"-1990 climatology.\n\nAn angular-distance weighting approach was used"
        u" to interpolate the station data onto the required grid. We chose to "
        u"grid the station anomalies to overcome some of the issues associated "
        u"with elevation dependence.\n\nThe data are available as gridded "
        u"anomalies, relative to the 1961-90 base period, and also as gridded "
        u"actual temperatures. The actual temperatures were created by gridding"
        u" the daily normals and adding these to the relevant daily anomaly.\n"
        u"\nSource: http://www.metoffice.gov.uk/hadobs/hadghcnd/index.html\n\n"
        u"Raw data file: {}")

    def extract_band(self, ncfile, band, outname, projection=None):
        """
        Extract specified band from NetCDF file and convert to GeoTIFF,
        using a VRT file to swap E-W axis
        :param ncfile: NetCDF input filename, formatted for use in GDAL
        :param band: Band number to process
        :param outname: Output GeoTIFF filename
        :param projection: Projection to use
        :return: Full pathname of output GeoTIFF
        """
        temp_vrt = os.path.join(self.tmp_dir, outname + '.vrt')
        try:
            source_xml = """
            <root>
                <SimpleSource>
                  <SourceFilename relativeToVRT="1">{fname}</SourceFilename>
                  <SourceBand>{band}</SourceBand>
                  <SrcRect xOff="48" yOff="0" xSize="96" ySize="73"/>
                  <DstRect xOff="0" yOff="0" xSize="96" ySize="73"/>
                </SimpleSource>
                <SimpleSource>
                  <SourceFilename relativeToVRT="1">{fname}</SourceFilename>
                  <SourceBand>{band}</SourceBand>
                  <SrcRect xOff="0" yOff="0" xSize="96" ySize="73"/>
                  <DstRect xOff="48" yOff="0" xSize="96" ySize="73"/>
                </SimpleSource>
            </root>
            """.format(fname=ncfile, band=band)
            geotransform = ','.join(['-1.818750000000000000e+02',
                                     '3.7500000000000000e+00',
                                     '0.0000000000000000e+00',
                                     '9.1250000000000000e+01',
                                     '0.0000000000000000e+00',
                                     '-2.5000000000000000e+00'])
            create_band_vrt(ncfile, temp_vrt, [band], source_xml,
                            projection=projection, geotransform=geotransform)
            gdal_translate(temp_vrt,
                           os.path.join(self.tmp_dir, outname),
                           projection='EPSG:4326',
                           options=['TILED=YES', 'COMPRESS=LZW'])
        finally:
            if os.path.exists(temp_vrt):
                os.remove(temp_vrt)

        return os.path.join(self.tmp_dir, outname)

    def get_date(self, days):
        """
        Calculate the date from the NetCDF band time value in days since 0/0/00
        :param days: Days since 00/00/00
        :return: Python date object
        """
        start = date(1, 1, 1)
        return start + relativedelta(days=days-2) + relativedelta(years=-1)

    def run(self):
        """
        Retrieve and process the HadGHCND climate data.
        """
        for key in self.layers.keys():
            src = os.path.join(self.base_url, key)
            tarfile = self.download(src)
            cdf_files = untar(os.path.join(self.tmp_dir, tarfile), self.tmp_dir)
            for cdf in cdf_files:
                for measure in ('tmin', 'tmax'):
                    ncds_gdal_name = 'NETCDF:{}:{}'.format(cdf, measure)
                    ncds = gdal.Open(ncds_gdal_name)
                    bands = ncds.RasterCount
                    layer_name = self.layers[key]['name'].format(
                        prefix=self.prefix, measure=measure
                    )
                    img_list = self.get_mosaic_filenames(layer_name)
                    files = []
                    for band in range(1, min(11, bands + 1)):
                        days = int(ncds.GetRasterBand(band)
                                   .GetMetadata()['NETCDF_DIM_time'])
                        band_date = re.sub('[\-\.]+', '',
                                           self.get_date(days).isoformat())
                        img_name = '{}_{}T000000000Z.tif'.format(layer_name,
                                                                 band_date)
                        if img_name not in img_list:
                            band_tif = self.extract_band(ncds_gdal_name,
                                                         band,
                                                         img_name,
                                                         projection='WGS84')
                            dst_file = self.data_dir.format(gsd=GS_DATA_DIR,
                                                            ws=self.workspace,
                                                            layer=layer_name,
                                                            file=img_name)
                            dst_dir = os.path.dirname(dst_file)
                            if not os.path.exists(dst_dir):
                                os.makedirs(dst_dir)
                            shutil.move(band_tif, dst_file)
                            files.append(dst_file)
                    sleep(RSYNC_WAIT_TIME * 2)
                    for file in files:
                        self.post_geoserver(file, layer_name, sleeptime=0)
                    style = '_'.join(layer_name.split('_')[0:2])
                    if not style_exists(layer_name):
                        with open(os.path.join(script_dir,
                                               'resources/{}.sld'.format(
                                                   style))) as sld:
                            self.set_default_style(layer_name,
                                                   layer_name,
                                                   sld.read())
                    title = self.layers[key]['title'].format(measure=measure)
                    self.update_geonode(layer_name,
                                        title=title,
                                        description=self.abstract.format(src),
                                        store=layer_name,
                                        bounds=('-180.0', '180.0',
                                                '-90.0', '90.0',
                                                'EPSG:4326'))
                    self.truncate_gs_cache(layer_name)
            self.cleanup()


if __name__ == '__main__':
    processor = HadGHCNDProcessor()
    processor.run()
