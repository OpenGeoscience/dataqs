import datetime
import os
import subprocess
from geoserver.catalog import Catalog
import psycopg2
import re
import sys
from StringIO import StringIO
from fiona import crs
import rasterio
from osgeo import gdal
from rasterio._warp import RESAMPLING
from rasterio.warp import calculate_default_transform, reproject
from geonode.geoserver.helpers import ogc_server_settings
import ogr2ogr


class GdalErrorHandler(object):
    """
    Don't display GDAL warnings, only errors
    """
    def __init__(self):
        self.err_level=gdal.CE_Failure
        self.err_no=0
        self.err_msg=''

    def handler(self, err_level, err_no, err_msg):
        self.err_level=err_level
        self.err_no=err_no
        self.err_msg=err_msg


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
    return datafile.RasterCount


def gdal_translate(src_filename, dst_filename, dst_format="GTiff", bands=None,
                   nodata=None, projection=None, options=None):
    """
    Convert a raster image with the specified arguments
    (as if running from commandline)
    :param argstring: command line arguments as string
    :return: Result of gdal_translate process (success or failure)
    """
    from osgeo import gdal
    from osr import SpatialReference

    if not options:
        options = []

    # Open existing dataset, subsetting bands if necessary
    if bands:
        tmp_file = src_filename + ".sub"
        gdal_band_subset(src_filename, bands, tmp_file)
        src_ds = gdal.Open(tmp_file)
    else:
        src_ds = gdal.Open(src_filename)
    try:
        #Open output format driver, see gdal_translate --formats for list
        driver = gdal.GetDriverByName(dst_format)

        #Output to new format
        dst_ds = driver.CreateCopy(dst_filename, src_ds, 0, options)

        if projection:
            srs = SpatialReference()
            srs.SetWellKnownGeogCS(projection)
            dst_ds.SetProjection(srs.ExportToWkt())

        if nodata is not None:
            band = dst_ds.GetRasterBand(1)
            band.SetNoDataValue(nodata)

    finally:
        #Properly close the datasets to flush to disk
        dst_ds = None
        src_ds = None
        band = None
        if bands and tmp_file:
            os.remove(tmp_file)


def cdo_invert(filename):
    """
    Invert a NetCDF image so that gdal_translate can read it.
    :param filename: Full path * name of NetCDF image to invert
    """
    output_file = "{}.inv.nc".format(filename)
    subprocess.check_call(["cdo", "invertlat", "{}.nc".format(
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
    finally:
        cur.close()
        conn.close()


def purge_old_data(table, datefield, days):
    """
    Remove data older than x days from a table
    """
    today = datetime.date.today()
    cutoff = (today - datetime.timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
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
    layer = gs_catalog.get_resource(layer_name,
                                    store=store,
                                    workspace=workspace)
    return layer is not None


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
    :param nodata: NoDataValue for raster bands (default is None
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
        #Properly close the datasets to flush to disk
        band = None
        inband = None
        outBand = None
        ds = None
        out_ds = None


def warp_image(infile, outfile, dst_crs="EPSG:3857", dst_driver='GTiff'):
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