from __future__ import absolute_import

import logging
import os
from dataqs.processor_base import GeoDataProcessor
from dataqs.helpers import get_band_count, gdal_translate, cdo_invert, \
    nc_convert, style_exists

logger = logging.getLogger("dataqs.processors")

SPEI_SLD="""<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>{name}</sld:Name>
    <sld:UserStyle>
      <sld:Name>{name}</sld:Name>
      <sld:Title>SPEI Drought Index</sld:Title>
      <sld:FeatureTypeStyle>
        <sld:Name>spei03_inv_a1c0d6fd</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#000000" opacity="0" quantity="-1000.0" label="No Data"/>
              <sld:ColorMapEntry color="#8B1A1A" opacity="1" quantity="-2.33" label="-2.33 or lower"/>
              <sld:ColorMapEntry color="#DE2929" opacity="1" quantity="-1.65" label="-1.65"/>
              <sld:ColorMapEntry color="#F3641D" opacity="1" quantity="-1.28" label="-1.28"/>
              <sld:ColorMapEntry color="#FDC404" opacity="1" quantity="-0.84" label="-0.84"/>
              <sld:ColorMapEntry color="#9AFA94" opacity="1" quantity="0" label="0"/>
              <sld:ColorMapEntry color="#03F2FD" opacity="1" quantity="0.84" label="0.84"/>
              <sld:ColorMapEntry color="#12ADF3" opacity="1" quantity="1.28" label="1.28"/>
              <sld:ColorMapEntry color="#1771DE" opacity="1" quantity="1.65" label="1.65"/>
              <sld:ColorMapEntry color="#00008B" opacity="1" quantity="2.33" label="2.33 or higher"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
"""

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
                self.set_default_style(layer_name, layer_name, SPEI_SLD.format(
                    name=layer_name
                ))
            self.update_geonode(layer_name, title=self.spei_files[layer_name])
            self.truncate_gs_cache(layer_name)
            self.cleanup()


if __name__ == '__main__':
    processor = SPEIProcessor()
    processor.run()
