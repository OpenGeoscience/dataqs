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

logger = logging.getLogger("dataqs.processors")

GPM_ACCOUNT = getattr(settings, 'GPM_ACCOUNT', 'anonymous')
GS_DATA_DIR = getattr(settings, 'GS_DATA_DIR', '/data/geodata')
GS_TMP_DIR = getattr(settings, 'GS_TMP_DIR', '/tmp')


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

    def download(self, filename=None, auth_account=GPM_ACCOUNT,
                 tmp_dir=GS_TMP_DIR, days=1):

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

    def run(self, days=1):

        tifs = self.download(days=days)

        for tif_file in tifs:
            layer_title, imgtime = self.parse_name(tif_file)

            time_format = imgtime.strftime('%Y%m%dT%H0000000Z')
            tif_out = "{prefix}_{time}.tif".format(
                    prefix=self.layer_name,
                    time=time_format)

            # Use gdal_translate to embed projection info
            gdal_translate(os.path.join(self.tmp_dir, tif_file),
                           os.path.join(self.tmp_dir, tif_out),
                           nodata=0, projection="EPSG:4326")

            dst_file = self.data_dir.format(gsd=GS_DATA_DIR, ws=self.workspace,
                                            layer=self.layer_name, file=tif_out)
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
                            bounds=('-180.0', '180.0', '-90.0', '90.0',
                                    'EPSG:4326'))
        self.truncate_gs_cache(self.layer_name)
        self.cleanup()


if __name__ == '__main__':
    processor = GPMProcessor()
    processor.run()
