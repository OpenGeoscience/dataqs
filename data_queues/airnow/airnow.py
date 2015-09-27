from __future__ import absolute_import

from ftplib import FTP
import logging
import os
import datetime
import re
import shutil
from django.conf import settings
from ..processor_base import GeoDataMosaicProcessor
from ..helpers import gdal_translate

logger = logging.getLogger("data_queues.processors")

AIRNOW_ACCOUNT = getattr(settings, 'AIRNOW_ACCOUNT', 'anonymous:anonymouse')
GS_DATA_DIR = getattr(settings, 'GS_DATA_DIR', '/data/geodata')
GS_TMP_DIR = getattr(settings, 'GS_TMP_DIR', '/tmp')


class AirNowGRIB2HourlyProcessor(GeoDataMosaicProcessor):
    """
    Class for processing hourly GRIB2 Air Quality Index raster
    time-series images from the AirNow API.
    (http://www.airnowapi.org/docs/AirNowMappingFactSheet.pdf)
    """
    prefix = "airnow_aqi_grib2_"
    base_url = "ftp://ftp.airnowapi.org/GRIB2/"
    hourly_layernames = ["ozone", "pm25", "combined"]
    hourly_patterns = ["", "_pm25", "_combined"]

    def download(self, filename=None, auth_account=AIRNOW_ACCOUNT,
                  days=1):

        ftp = FTP(self.base_url)
        ftp.login(auth_account, auth_account)
        file_list = ftp.nlst()

        dl_files = []

        for pattern in self.hourly_patterns:
            hourly_pattern = ("US-\d{8}{}\.grib2".format(pattern) if days == 1
                              else "US-\d{6}12{}*\.grib2".format(pattern))

            re_1day = re.compile(hourly_pattern)

            files = sorted([x for x in file_list if re_1day.search(x)])[-days:]

            for file_1day in files:
                with open(os.path.join(self.tmp_dir, file_1day), 'wb') as outfile:
                    ftp.retrbinary('RETR %s' % file_1day, outfile.write)
                dl_files.append[file_1day]

        return files

    def convert(self, img_file):
        basename = os.path.splitext(img_file)[0]

        gdal_warp


    def run(self, days=1):

        tifs = self.download(days=days)

        for tif_file in tifs:
            layer_title, imgtime = self.parse_name(tif_file)

            time_format = imgtime.strftime('%Y%m%dT%H0000000Z')
            tif_out = "{prefix}_{time}.tif".format(
                    prefix=self.layer_name,
                    time=time_format)

            # Use gdal_translate to embed projection info
            gdal_translate(os.path.join(self.tmp_dir, tif_file), os.path.join(self.tmp_dir, tif_out),
                           nodata=0, projection="EPSG:4326")

            dst_file = self.data_dir.format(gsd=GS_DATA_DIR, ws=self.workspace, layer=self.layer_name, file=tif_out)
            dst_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            if dst_file.endswith('.tif'):
                shutil.move(os.path.join(self.tmp_dir, tif_out), dst_file)
                self.post_geoserver(dst_file, self.layer_name)

        layer_title, imgtime = self.parse_name(tifs[-1])
        self.drop_old_hourly_images(imgtime, self.layer_name)
        self.drop_old_daily_images(imgtime, self.layer_name)

        self.update_geonode(self.layer_name, title=layer_title,
                            bounds=('-180.0', '180.0', '-90.0', '90.0', 'EPSG:4326'))
        self.truncate_gs_cache(self.layer_name)
        self.cleanup()
