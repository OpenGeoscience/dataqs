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
import zipfile

from dataqs.helpers import gdal_translate, style_exists
from dataqs.processor_base import GeoDataProcessor

script_dir = os.path.dirname(os.path.realpath(__file__))


class LandscanProcessor(GeoDataProcessor):
    """
    Class for processing sample Landscan data
    """

    layer = "landscan"
    description = "LandScan 2011 Global Population Project"

    def get_landscan(self):
        """
        Downloads the sample landscan image for Cyprus
        """

        url = "http://web.ornl.gov/sci/landscan/landscan2011/LS11sample_Cyprus.zip"
        zip_dir = os.path.join(self.tmp_dir, "landscan.zip")
        urlretrieve(url, zip_dir)

        # Open up the zip file
        zip_ref = zipfile.ZipFile(zip_dir, 'r')
        landscan_dir = os.path.join(self.tmp_dir, "landscan")
        zip_ref.extractall(landscan_dir)
        zip_ref.close()

        return landscan_dir

    def convert_landscan(self, landscan_dir):
        """
        Converts arcgrid into a tiff file
        """

        # Important
        # The directory which holds the .adf files
        # needs to be found here

        for subdir, dirs, files in os.walk(landscan_dir):
            for d in dirs:
                if set([f.endswith('.adf') for f in os.listdir(os.path.join(subdir, d))]) == {True}:
                    grid_dir = os.path.join(subdir, d)

        src_ds = gdal.Open(grid_dir)
        src_ds.SetProjection('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        driver = gdal.GetDriverByName("GTiff")

        #Output to new format
        tiff_output = os.path.join(self.tmp_dir, "landscan.tiff")
        dst_ds = driver.CreateCopy(tiff_output, src_ds, 0)

        return tiff_output

    def import_landscan(self, landscan_tiff):
        """
        Imports landscan to geonode
        """

        self.post_geoserver(landscan_tiff, self.layer)
        if not style_exists(self.layer):
            with open(os.path.join(
                    script_dir, 'resources/landscan.sld')) as sld:
                self.set_default_style(self.layer,
                                       self.layer, sld.read())
        self.update_geonode(self.layer, title=self.layer,
                            store=self.layer,
                            description=self.description)
        self.truncate_gs_cache(self.layer)


    def run(self):
        """
        Retrieve and process Landscan sample data
        """

        landscan_dir = self.get_landscan()
        landscan_tiff = self.convert_landscan(landscan_dir)
        self.import_landscan(landscan_tiff)

if __name__ == '__main__':
    processor = LandscanProcessor()
    processor.run()
