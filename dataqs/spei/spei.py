from __future__ import absolute_import

import logging
import os
from dataqs.processor_base import GeoDataProcessor, DEFAULT_WORKSPACE
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
            self.download("{}{}.nc".format(self.base_url, layer_name))
            tif_file = self.convert(layer_name)
            self.post_geoserver(tif_file, layer_name)
            if not style_exists(layer_name):
                with open(os.path.join(script_dir,
                                       'resources/spei.sld')) as sld:
                    self.set_default_style(layer_name, layer_name, sld.read())
            self.update_geonode(layer_name, title=self.spei_files[layer_name],
                                store=layer_name)
            self.truncate_gs_cache(layer_name)
            self.cleanup()


if __name__ == '__main__':
    processor = SPEIProcessor()
    processor.run()
