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

import datetime
import gzip
import logging
import shutil
import tarfile
import traceback
import os
import subprocess
import requests
import psycopg2
import re
import sys
import unicodedata
import ogr2ogr
import rasterio
from osgeo import gdal, ogr
from osr import SpatialReference
import xml.etree.ElementTree as ET
from StringIO import StringIO
from rasterio.warp import RESAMPLING
from rasterio.warp import calculate_default_transform, reproject
from geonode.geoserver.helpers import ogc_server_settings
from geoserver.catalog import Catalog, FailedRequestError

logger = logging.getLogger("dataqs.helpers")


class GdalErrorHandler(object):
    """
    Don't display GDAL warnings, only errors
    """
    def __init__(self):
        self.err_level = gdal.CE_Failure
        self.err_no = 0
        self.err_msg = ''

    def handler(self, err_level, err_no, err_msg):
        self.err_level = err_level
        self.err_no = err_no
        self.err_msg = err_msg


err = GdalErrorHandler()
handler = err.handler
gdal.PushErrorHandler(handler)
gdal.UseExceptions()


def split_args(arg_string):
    """
    Split a string into a list based on whitespace, unless enclosed in quotes
    :param arg_string: Command-line arguments as string
    :return: list of strings
    """
    return [r.strip("\"") for r in re.findall(
        r'(?:"[^"]*"|[^\s"])+', arg_string)]


def get_band_count(raster_file):
    """
    Return the number of bands in a raster file
    :param raster_file: The full path & name of a raster file.
    :return: number of bands
    """
    datafile = gdal.Open(raster_file)
    count = datafile.RasterCount
    del datafile
    return count


def create_band_vrt(src, dst, bands, source_str, nodata=None, projection=None,
                    geotransform=None):
    """
    Create a VRT file for an image by band.
    :param src: Source raster filepath
    :param dst: Destination VRT filepath
    :param bands: list of band numbers
    :param source_str: String version of 'Source' XML elements
    :param nodata: NoData value for output
    :param projection: Projection of output
    :param geotransform: Geotransform string for output
    """
    gdal_translate(src, dst,
                   bands=bands, nodata=nodata, of='vrt', projection=projection)
    tree = ET.parse(dst)
    root = tree.getroot()
    if geotransform:
        gt = root.find('GeoTransform')
        gt.text = geotransform
    sources = ET.fromstring(source_str).getchildren()
    bands = root.findall('VRTRasterBand')
    for band in bands:
        for source in sources:
            band.append(source)
    tree.write(dst, encoding='utf-8')


def gdal_translate(src_filename, dst_filename, of="GTiff", bands=None,
                   nodata=None, projection=None, options=None):
    """
    Convert a raster image with the specified arguments
    (as if running from commandline)
    """
    if not options:
        options = []

    # Open existing dataset, subsetting bands if necessary

    src_ds = gdal.Open(src_filename)
    try:
        # Open output format driver, see gdal_translate --formats for list
        driver = gdal.GetDriverByName(of)

        # Output to new format
        if bands:
            dst_ds = driver.Create(dst_filename, src_ds.RasterXSize,
                                   src_ds.RasterYSize, len(bands),
                                   src_ds.GetRasterBand(bands[0]).DataType)

            dst_ds.SetMetadata(src_ds.GetMetadata())
            for idx, band_num in enumerate(bands):
                inband = src_ds.GetRasterBand(band_num).ReadAsArray()
                outBand = dst_ds.GetRasterBand(idx + 1)
                outBand.WriteArray(inband)
                outBand.SetMetadata(outBand.GetMetadata())
                if nodata is not None:
                    outBand.SetNoDataValue(nodata)
                else:
                    outBand.SetNoDataValue(
                        src_ds.GetRasterBand(band_num).GetNoDataValue())
                inband = None
                outBand = None
        else:
            dst_ds = driver.CreateCopy(dst_filename, src_ds, 0, options)
            if nodata is not None:
                band = dst_ds.GetRasterBand(1)
                band.SetNoDataValue(nodata)

        dst_ds.SetGeoTransform(src_ds.GetGeoTransform())

        if projection:
            srs = SpatialReference()
            srs.SetWellKnownGeogCS(projection)
            dst_ds.SetProjection(srs.ExportToWkt())

    finally:
        # Properly close the datasets to flush to disk
        dst_ds = None
        src_ds = None
        band = None


def gunzip(filepath):
    """
    Gunzip a file.
    :param filepath: Filepath of gzipped file
    :return: Name of output file
    """
    outfile = filepath.rstrip('.gz')
    with gzip.open(filepath) as gfile, open(outfile, 'wb') as ucfile:
        shutil.copyfileobj(gfile, ucfile)
    return outfile


def untar(filepath, outpath=''):
    """
    Extract contents of a tar file to a specified directory
    :param filepath: Filepath of tar file
    :param outpath: Output directory
    :return:
    """
    files = []
    tf = tarfile.open(filepath)
    for item in tf:
        tf.extract(item, outpath)
        files.append(os.path.join(outpath, item.name))
    return files


def nc_convert(filename):
    """
    Transform a NETCDF4 file to classic-model format.
    Requires installation of netcdf binaries:
    apt-get install netcdf-bin (Ubuntu) or brew install netcdf (OSX)
    :param filename:
    :return: output filename
    """
    output_file = re.sub('\.nc$', '.classic.nc', filename)
    subprocess.check_call(
        ["nccopy", "-k", "classic", filename, output_file])
    return output_file


def cdo_invert(filename):
    """
    Invert a NetCDF image so that gdal_translate can read it.
    Requires installation of cdo (Climate Data Operators).
    apt-get install cdo (Ubuntu) or brew install cdo (OSX)
    :param filename: Full path * name of NetCDF image to invert
    :return: output filename
    """

    output_file = "{}.inv.nc".format(os.path.splitext(filename)[0])
    subprocess.check_call(["cdo", "invertlat", "{}".format(
        filename), output_file])
    return output_file


def cdo_fixlng(filename, bounds="-180,180,-90,90"):
    """
    Change the longitude coordinates of a NetCDF file from 0->360 to -180->180
    :param filename: Full path * name of NetCDF image to process
    :param bounds: String representation of bounds (minX,maxX,minY,maxY)
    :return: output filename
    """

    output_file = "{}.lng.nc".format(os.path.splitext(filename)[0])
    subprocess.check_call(["cdo", "sellonlatbox,{}".format(bounds), "{}".format(
        filename), output_file])
    return output_file


def ogr2ogr_exec(argstring):
    """
    Run an ogr2ogr command
    :param argstring: command line arguments as string
    :return: success or failure
    """
    args = ["", ]
    args.extend(split_args(argstring))
    old_stdout = sys.stdout
    result = StringIO()
    sys.stdout = result
    try:
        foo = ogr2ogr.main(args)
        if not foo:
            raise Exception(result.getvalue())
    finally:
        if old_stdout:
            sys.stdout = old_stdout


def postgres_query(query, commit=False, returnable=False, params=None):
    """
    Execute a PostgreSQL query
    :param query: Query string to execute
    :param commit: Whether or not to commit the query
    :param returnable: Whether or not to return results
    :return: Query result set or None
    """
    db = ogc_server_settings.datastore_db
    conn_string = (
        "dbname={dbname} user={dbuser} host={dbhost} password={dbpass}".format(
            dbname=db["NAME"], dbuser=db["USER"],
            dbhost=db["HOST"], dbpass=db["PASSWORD"]
        )
    )
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        if returnable:
            return cur.fetchall()
        if commit:
            conn.commit()
        return None
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error(query)
        logger.error(params)
        raise e
    finally:
        cur.close()
        conn.close()


def purge_old_data(table, datefield, days):
    """
    Remove data older than x days from a table
    """
    today = datetime.date.today()
    cutoff = (today - datetime.timedelta(days=days)).strftime(
        "%Y-%m-%d 00:00:00")
    postgres_query('DELETE FROM {} where CAST("{}" as timestamp) < %s;'.format(
        table, datefield), commit=True, params=(cutoff,))


def table_exists(tablename):
    """
    Determine if a table/view already exists
    :param tablename:
    :return:
    """
    db_query = postgres_query("SELECT EXISTS " +
                              "(SELECT 1 FROM information_schema.tables " +
                              "WHERE table_name = '{}');".format(tablename),
                              returnable=True)
    if db_query and db_query[0][0]:
        return True
    return False


def layer_exists(layer_name, store, workspace):
    _user, _password = ogc_server_settings.credentials
    url = ogc_server_settings.rest
    gs_catalog = Catalog(url, _user, _password)
    try:
        layer = gs_catalog.get_resource(layer_name, store=store,
                                        workspace=workspace)
        return layer is not None
    except FailedRequestError:
        return False


def style_exists(style_name):
    _user, _password = ogc_server_settings.credentials
    url = ogc_server_settings.rest
    gs_catalog = Catalog(url, _user, _password)
    style = gs_catalog.get_style(style_name)
    return style is not None


def gdal_band_subset(infile, bands, dst_filename, dst_format="GTiff"):
    """
    Create a new raster image containing only the specified bands
    from input image  **NOTE: numpy must be installed before GDAL to use
    the ReadAsArray, WriteArray methods
    :param infile: inpur raster image
    :param bands: list of bands in input image to copy
    :param dst_filename: destination image filename
    :param dst_format: destination image format (default is GTiff)
    """
    ds = gdal.Open(infile)
    driver = gdal.GetDriverByName(dst_format)
    driver.Register()
    band = bands[0]
    out_ds = driver.Create(dst_filename, ds.RasterXSize,
                           ds.RasterYSize, len(bands),
                           ds.GetRasterBand(band).DataType)
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    try:
        for idx, band_num in enumerate(bands):
            inband = ds.GetRasterBand(band_num).ReadAsArray()
            outBand = out_ds.GetRasterBand(idx+1)
            outBand.WriteArray(inband)
            inband = None
            outBand = None

    finally:
        # Properly close the datasets to flush to disk
        band = None
        inband = None
        outBand = None
        ds = None
        out_ds = None


def warp_image(infile, outfile, dst_crs="EPSG:3857", dst_driver='GTiff'):
    """
    Use rasterio to warp an image from one projection to another
    :param infile: Origina raster image
    :param outfile: Warped raster image
    :param dst_crs: Output projection
    :param dst_driver: Output filetype driver
    :return: None
    """
    with rasterio.drivers(CPL_DEBUG=False):
        with rasterio.open(infile) as src:
            res = None
            dst_transform, dst_width, dst_height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height,
                *src.bounds, resolution=res)
            out_kwargs = src.meta.copy()
            out_kwargs.update({
                'crs': dst_crs,
                'transform': dst_transform,
                'affine': dst_transform,
                'width': dst_width,
                'height': dst_height,
                'driver': dst_driver
            })

            with rasterio.open(outfile, 'w', **out_kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.affine,
                        src_crs=src.crs,
                        dst_transform=out_kwargs['transform'],
                        dst_crs=out_kwargs['crs'],
                        resampling=RESAMPLING.nearest,
                        num_threads=1)


def get_html(url=None):
    """
    Make a standard GET request and return the response content
    :param url: URL to get
    :return: Response content
    """
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def asciier(txt):
    """
    Replace any non-ASCII characters
    """
    norm_txt = re.sub('\s+', ' ', unicodedata.normalize('NFD', txt))
    ascii_txt = norm_txt.encode('ascii', 'ignore').decode('ascii')
    return ascii_txt


class MockResponse(object):
    """
    Mock requests.Response object with canned content
    """
    def __init__(self, content):
        self.content = content
        self.text = self.content
        self.status_code = 200

    def raise_for_status(self):
        pass


def add_keywords(keyword_list, extra_keywords):
    """Adds extra_keywords list to the keyword_list"""

    # check if datetime and category already exist in the
    # keyword list
    filtered_keywords = [k for k in keyword_list if not
                         (k.startswith('category:') or
                          k.startswith('datetime:') or
                          k.startswith('layer_info'))]

    return filtered_keywords + extra_keywords


def _getMinMax(layer, field):
    min_value, max_value = float('inf'), float('-inf')
    for f in layer:
        value = f.GetField(field)
        if value < min_value:
            min_value = value
        if value > max_value:
            max_value = value

    return {'properties': {'min': min_value, 'max': max_value},
            'type': 'numeric'}


def _getNumericFields(layer):
    """ Gets only the numeric fields from layer"""

    layerDefinition = layer.GetLayerDefn()
    numFields = []
    for i in xrange(layerDefinition.GetFieldCount()):
        fieldName = layerDefinition.GetFieldDefn(i).GetName()
        fieldTypeCode = layerDefinition.GetFieldDefn(i).GetType()
        fieldDef = layerDefinition.GetFieldDefn(i)
        fieldType = fieldDef.GetFieldTypeName(fieldTypeCode)
        if fieldType != 'String':
            numFields.append(fieldName)

    return numFields


def get_vector_layer_info(geojson):
    """ Gets information about a given geojson file """

    dataSource = ogr.Open(geojson)
    layer = dataSource.GetLayer()
    geom = {0: 'polygon', 1: 'point', 2: 'line',
            3: 'polygon', 4: 'polygon', 5: 'polygon',
            6: 'polygon', -2147483647: 'point'}

    subType = geom[layer.GetGeomType()]
    count = layer.GetFeatureCount()
    numFields = _getNumericFields(layer)
    info = {'layerType': 'vector', 'subType': subType}
    attr = {}
    for f in numFields:
        prop = _getMinMax(layer, f)
        prop['properties']['count'] = count
        attr[f.lower()] = prop
        layer.ResetReading()
    dataSource = None
    info['attributes'] = attr
    return info
