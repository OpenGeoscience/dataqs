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
from dataqs.processor_base import GeoDataProcessor
from dataqs.helpers import get_band_count, gdal_translate, cdo_invert, \
    nc_convert, style_exists

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class SPEIProcessor(GeoDataProcessor):
    """
    Class for processing data from the SPEI Global Drought Monitor
    (http://sac.csic.es/spei/map/maps.html)
    """
    prefix = "spei"
    spei_files = {
        'spei01': 'SPEI Global Drought Monitor (past month)',
        'spei03': 'SPEI Global Drought Monitor (past 3 months)'}
    base_url = "http://notos.eead.csic.es/spei/nc/"
    description = (
        u"The SPEI Global Drought Monitor (http://sac.csic.es/spei) offers near"
        u" real-time information about drought conditions at the global scale, "
        u"with a 0.5 degrees spatial resolution and a monthly time resolution. "
        u"SPEI time-scales between 1 & 48 months are provided. The calibration"
        u" period for the SPEI is January 1950 to December 2010.\n\nThe dataset"
        u" is updated during the first days of the following month based on the"
        u" most reliable and updated sources of climatic data. Mean temperature"
        u" data are obtained from the NOAA NCEP CPC GHCN_CAMS gridded dataset. "
        u"Monthly precipitation sums data are obtained from the Global "
        u"Precipitation Climatology Centre (GPCC). Data from the 'first guess' "
        u"GPCC product, with an original resolution of 1º, are interpolated to "
        u"the resolution of 0.5º.\n\nCurrently, the SPEI Global Drought Monitor"
        u" is based on the Thortnthwaite equation for estimating potential "
        u"evapotranspiration, PET. This is due to the lack of real-time data "
        u"sources for computing more robust PET estimations which have larger "
        u"data requirements. The main advantage of the SPEI Global Drought "
        u"Monitor is thus its near real-time character, a characteristic best "
        u"suited for drought monitoring and early warning purposes. For long-"
        u"term analysis, however, other datasets are to be preferred that rely "
        u"on more robust methods of PET estimation. Use of the SPEIbase dataset"
        u", which is based on the FAO-56 Penman-Monteith model, is thus "
        u"recommended for climatological studies of drought.\n\nSource: http://"
        u"notos.eead.csic.es/spei/nc/"
    )

    def convert(self, nc_file):
        tif_file = "{}.tif".format(nc_file)
        nc_transform = nc_convert(os.path.join(self.tmp_dir, nc_file))
        cdo_transform = cdo_invert(os.path.join(self.tmp_dir, nc_transform))
        band = get_band_count(cdo_transform)
        gdal_translate(cdo_transform, os.path.join(self.tmp_dir, tif_file),
                       bands=[band], projection='EPSG:4326')
        return tif_file

    def run(self):
        """
        Retrieve and process all SPEI image files listed in the SPEIProcess
        object's spei_files property.
        """
        for layer_name in self.spei_files.keys():
            dlfile = self.download("{}{}.nc".format(self.base_url, layer_name))
            tif_file = self.convert(dlfile)
            self.post_geoserver(tif_file, layer_name)
            if not style_exists(layer_name):
                with open(os.path.join(script_dir,
                                       'resources/spei.sld')) as sld:
                    self.set_default_style(layer_name, layer_name, sld.read())
            self.update_geonode(layer_name,
                                title=self.spei_files[layer_name],
                                description=self.description,
                                store=layer_name,
                                extra_keywords=['category:Agriculture'])
            self.truncate_gs_cache(layer_name)
            self.cleanup()


if __name__ == '__main__':
    processor = SPEIProcessor()
    processor.run()
