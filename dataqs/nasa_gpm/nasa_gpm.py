from __future__ import absolute_import

from ftplib import FTP
import logging
import os
import datetime
import re
import shutil
from django.conf import settings
from dataqs.processor_base import GeoDataMosaicProcessor
from dataqs.helpers import gdal_translate, style_exists

logger = logging.getLogger("dataqs.processors")

GPM_ACCOUNT = getattr(settings, 'GPM_ACCOUNT', 'anonymous')
GS_DATA_DIR = getattr(settings, 'GS_DATA_DIR', '/data/geodata')
GS_TMP_DIR = getattr(settings, 'GS_TMP_DIR', '/tmp')

GPM_SLD="""<?xml version="1.0" encoding="UTF-8"?><sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>nasa_gpm</sld:Name>
    <sld:UserStyle>
      <sld:Name>nasa_gpm</sld:Name>
      <sld:Title>NASA GPM Precipitation Estimate</sld:Title>
      <sld:IsDefault>1</sld:IsDefault>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#000000" opacity="0" quantity="-1" label="No Data"/>
              <sld:ColorMapEntry color="#110AF5" opacity="1" quantity="10" label="1 mm"/>
              <sld:ColorMapEntry color="#166CDE" opacity="1" quantity="50" label="5 mm"/>
              <sld:ColorMapEntry color="#12EFD9" opacity="1" quantity="100" label="10 mm"/>
              <sld:ColorMapEntry color="#30B60E" opacity="1" quantity="250" label="25/mm"/>
              <sld:ColorMapEntry color="#F6EE09" opacity="1" quantity="500" label="50 mm"/>
              <sld:ColorMapEntry color="#F3830A" opacity="1" quantity="750" label="75 mm"/>
              <sld:ColorMapEntry color="#F41708" opacity="1" quantity="1000" label="100 mm"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
"""

class GPMProcessor(GeoDataMosaicProcessor):
    """
    Class for processing the latest NASA IMERG Rainfall estimates combining data
    from all passive-microwave instruments in the GPM Constellation.  Uses the 'early'
    (possibly less accurate) images for most timely information (generated within 6-8
    hours of observation).
    """

    base_url = "jsimpson.pps.eosdis.nasa.gov"
    layername_prefix = 'nasa_gpm_'
    prefix = '3B-HHR-E.MS.MRG.3IMERG.'
    layer_name = 'nasa_gpm_24hr'
    archive_hours = ("T12:00:00.000Z", "T12:30:00.000Z")

    def download(self, auth_account=GPM_ACCOUNT, tmp_dir=GS_TMP_DIR, days=1):
        ftp = FTP(self.base_url)
        ftp.login(auth_account, auth_account)
        ftp.cwd('/NRTPUB/imerg/gis/early')
        file_list = ftp.nlst()
        pattern = '.+\.1day\.tif' if days == 1 else '.+\-S120000\-.+\.1day\.tif'
        re_1day = re.compile(pattern)
        files = sorted([x for x in file_list if re_1day.search(x)])[-days:]
        for file_1day in files:
            with open(os.path.join(self.tmp_dir, file_1day), 'wb') as outfile:
                ftp.retrbinary('RETR %s' % file_1day, outfile.write)

            tfw_file = file_1day.replace('.tif', '.tfw')
            with open(os.path.join(self.tmp_dir, tfw_file), 'wb') as outfile:
                ftp.retrbinary('RETR %s' % tfw_file, outfile.write)
        return files

    def parse_name(self, tifname):
        name_subs = re.search(
            'IMERG\.(\d{8}-S\d{6}).+\.(3hr|30min|1day)\.tif', tifname)
        imgtime = datetime.datetime.strptime(name_subs.group(1),
                                             "%Y%m%d-S%H%M%S")
        imgstrtime = imgtime.strftime("%Y-%m-%d %H:00")
        layer_title = "NASA Global Precipitation Estimate ({}) - {} UTC".format(
            name_subs.group(2), imgstrtime)
        return layer_title, imgtime

    def convert(self, tif_file):
        layer_title, imgtime = self.parse_name(tif_file)
        time_format = imgtime.strftime('%Y%m%dT%H0000000Z')
        tif_out = "{prefix}_{time}.tif".format(
                prefix=self.layer_name,
                time=time_format)
        # Use gdal_translate to embed projection info
        gdal_translate(os.path.join(self.tmp_dir, tif_file),
                       os.path.join(self.tmp_dir, tif_out),
                       nodata=0, projection="EPSG:4326")

        return tif_out

    def run(self, days=1):
        tifs = self.download(days=days)
        for tif_file in tifs:
            projected_tif = self.convert(tif_file)
            dst_file = self.data_dir.format(gsd=GS_DATA_DIR, ws=self.workspace,
                                            layer=self.layer_name,
                                            file=projected_tif)
            dst_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            if dst_file.endswith('.tif'):
                shutil.move(os.path.join(self.tmp_dir, projected_tif), dst_file)
                self.post_geoserver(dst_file, self.layer_name)

        layer_title, imgtime = self.parse_name(tifs[-1])
        self.drop_old_hourly_images(imgtime, self.layer_name)
        self.drop_old_daily_images(imgtime, self.layer_name)
        if not style_exists(self.layer_name):
            self.set_default_style(self.layer_name, self.layer_name, GPM_SLD)
        self.update_geonode(self.layer_name, title=layer_title,
                            store=self.layer_name,
                            bounds=('-180.0', '180.0', '-90.0', '90.0',
                                    'EPSG:4326'))
        self.truncate_gs_cache(self.layer_name)
        self.cleanup()


if __name__ == '__main__':
    processor = GPMProcessor()
    processor.run()
