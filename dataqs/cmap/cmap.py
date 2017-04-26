from __future__ import absolute_import
import logging
import os
import re
import shutil
from datetime import date
from ftplib import FTP
from time import sleep
from dateutil.relativedelta import relativedelta
from dataqs.processor_base import GeoDataMosaicProcessor, GS_DATA_DIR, \
    GS_TMP_DIR, RSYNC_WAIT_TIME
from dataqs.helpers import get_band_count, gdal_translate, \
    nc_convert, style_exists, cdo_fixlng

logger = logging.getLogger("dataqs.processors")
script_dir = os.path.dirname(os.path.realpath(__file__))


class CMAPProcessor(GeoDataMosaicProcessor):
    """
    Processor for Land-Ocean Temperature Index, ERSSTv4, 1200km smoothing
    from the NASA Goddard Institute for Space Studies' Surface Temperature
    Analysis (GISTEMP).
    More info at http://data.giss.nasa.gov/gistemp/
    """
    prefix = "cmap"
    base_url = "ftp.cdc.noaa.gov"
    base_path = "/Datasets/cmap/enh/"
    base_name = "precip.mon.mean.nc"
    layer_name = 'cmap'
    bounds = '-178.75,178.75,-88.75,88.75'
    title = 'CPC Merged Analysis of Precipitation, 1979/01 - {}'
    abstract = (
        "The CPC Merged Analysis of Precipitation ('CMAP') is a technique which"
        " produces pentad and monthly analyses of global precipitation in which"
        " observations from raingauges are merged with precipitation estimates "
        "from several satellite-based algorithms (infrared and microwave). The "
        "analyses are on a 2.5 x 2.5 degree latitude/longitude grid and extend "
        "back to 1979.\n\nThese data are comparable (but should not be confused"
        " with) similarly combined analyses by the Global Precipitation "
        "Climatology Project which are described in Huffman et al (1997).\n\n"
        "It is important to note that the input data sources to make these "
        "analyses are not constant throughout the period of record. For example"
        ", SSM/I (passive microwave - scattering and emission) data became "
        "available in July of 1987; prior to that the only microwave-derived "
        "estimates available are from the MSU algorithm (Spencer 1993) which is"
        " emission-based thus precipitation estimates are avaialble only over "
        " oceanic areas. Furthermore, high temporal resolution IR data from "
        "geostationary satellites (every 3-hr) became available during 1986;"
        " prior to that, estimates from the OPI technique (Xie and Arkin 1997) "
        "are used based on OLR from polar orbiting satellites.\n\nThe merging "
        "technique is thoroughly described in Xie and Arkin (1997). Briefly, "
        "the methodology is a two-step process. First, the random error is "
        "reduced by linearly combining the satellite estimates using the "
        "maximum likelihood method, in which case the linear combination "
        "coefficients are inversely proportional to the square of the local "
        "random error of the individual data sources. Over global land areas "
        "the random error is defined for each time period and grid location by "
        "comparing the data source with the raingauge analysis over the "
        "surrounding area. Over oceans, the random error is defined by "
        "comparing the data sources with the raingauge observations over the "
        "Pacific atolls. Bias is reduced when the data sources are blended in "
        "the second step using the blending technique of Reynolds (1988). Here "
        "the data output from step 1 is used to define the \"shape\" of the "
        "precipitation field and the rain gauge data are used to constrain the "
        "amplitude.\n\nMonthly and pentad CMAP estimates back to the 1979 are "
        "available from CPC ftp server.\n\nSource: "
        "http://www.esrl.noaa.gov/psd/data/gridded/data.cmap.html\n\nRaw data "
        "file: ftp://ftp.cdc.noaa.gov/Datasets/cmap/enh/precip.mon.mean.nc"
        "\n\nReferences:\n\nHuffman, G. J. and "
        "co-authors, 1997: The Global Precipitation Climatology Project (GPCP) "
        "combined data set. Bull. Amer. Meteor. Soc., 78, 5-20.\n\nReynolds, R."
        " W., 1988: A real-time global sea surface temperature analysis. J. "
        "Climate, 1, 75-86.\n\nSpencer, R. W., 1993: Global oceanic "
        "precipitation from the MSU during 1979-91 and comparisons to other "
        "climatologies. J. Climate, 6, 1301-1326.\n\nXie P., and P. A. Arkin, "
        "1996: Global precipitation: a 17-year monthly analysis based on gauge "
        "observations, satellite estimates, and numerical model outputs. Bull. "
        "Amer. Meteor. Soc., 78, 2539-2558."
    )

    def download(self, url, tmp_dir=GS_TMP_DIR, filename=None):
        if not filename:
            filename = url.rsplit('/')[-1]
        ftp = FTP(self.base_url)
        ftp.login('anonymous', 'anonymous')
        ftp.cwd(self.base_path)
        with open(os.path.join(self.tmp_dir, filename),
                  'wb') as outfile:
            ftp.retrbinary('RETR %s' % self.base_name, outfile.write)
        return filename

    def convert(self, nc_file):
        nc_transform = nc_convert(nc_file)
        cdo_transform = cdo_fixlng(nc_transform, bounds=self.bounds)
        return cdo_transform

    def extract_band(self, tif, band, outname):
        outfile = os.path.join(self.tmp_dir, outname)
        gdal_translate(tif, outfile, bands=[band],
                       projection='EPSG:4326',
                       options=['TILED=YES', 'COMPRESS=LZW'])
        return outfile

    def get_date(self, months):
        start_month = date(1979, 1, 1)
        return start_month + relativedelta(months=months - 1)

    def get_title(self, months):
        end_month = self.get_date(months)
        return self.title.format(end_month.strftime('%Y/%m'))

    def run(self):
        """
        Retrieve and process the latest NetCDF file.
        """
        ncfile = self.download(
            self.base_url, filename='{}.nc'.format(self.layer_name))
        cdf_file = self.convert(os.path.join(self.tmp_dir, ncfile))
        bands = get_band_count(cdf_file)
        img_list = self.get_mosaic_filenames(self.layer_name)
        dst_files = []
        for band in range(1, bands + 1):
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
                    dst_files.append(dst_file)
        sleep(RSYNC_WAIT_TIME * 2)
        for dst_file in dst_files:
            self.post_geoserver(dst_file, self.layer_name, sleeptime=0)

        if not style_exists(self.layer_name):
            with open(os.path.join(script_dir,
                                   'resources/cmap.sld')) as sld:
                self.set_default_style(self.layer_name, self.layer_name,
                                       sld.read().format(latest_band=bands))
        self.update_geonode(
            self.layer_name, title=self.get_title(bands),
            description=self.abstract,
            store=self.layer_name,
            bounds=('-178.75', '178.75', '-88.75', '88.75',
                    'EPSG:4326'),
            extra_keywords=['category:Climatology Meteorology'])
        self.truncate_gs_cache(self.layer_name)
        self.cleanup()


if __name__ == '__main__':
    processor = CMAPProcessor()
    processor.run()
