from __future__ import absolute_import

import logging
import os
from ..processor_base import GeoDataProcessor
from ..helpers import get_band_count, gdal_translate, cdo_invert

logger = logging.getLogger("dataqs.processors")


class SPIEProcessor(GeoDataProcessor):
    """
    Class for processing data from the SPEI Global Drought Monitor
    (http://sac.csic.es/spei/map/maps.html)
    """
    prefix = "spei"
    spei_files = ('spei01', 'spei03')
    base_url = "http://notos.eead.csic.es/spei/nc/"

    def run(self):
        """
        Retrieve and process all SPEI image files listed in the SPEIProcess
        object's spei_files property.
        """
        for file in self.spei_files:
            self.download("{}{}.nc".format(self.base_url, file))
            tif_file = "{}.tif".format(file)
            cdo_transform = cdo_invert(os.path.join(self.tmp_dir, file))
            band = get_band_count(cdo_transform)
            gdal_translate(cdo_transform, os.path.join(self.tmp_dir, tif_file),
                           bands=[band], projection='EPSG:4326')
            self.post_geoserver(tif_file, file)
            self.update_geonode(file)
            self.truncate_gs_cache(file)
            self.cleanup()


if __name__ == '__main__':
    processor = SPIEProcessor()
    processor.run()
