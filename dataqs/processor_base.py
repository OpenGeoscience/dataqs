from __future__ import absolute_import

import glob
import json
import logging
from time import sleep
from urlparse import urljoin
from zipfile import ZipFile
from geoserver.catalog import Catalog
import os
import datetime
import requests
from django.conf import settings
import shutil
from geonode.geoserver.helpers import ogc_server_settings
from geonode.geoserver.management.commands.updatelayers import Command \
    as UpdateLayersCommand

logger = logging.getLogger("dataqs.processors")

DEFAULT_WORKSPACE = getattr(settings, 'DEFAULT_WORKSPACE', 'geonode')
GS_DATA_DIR = getattr(settings, 'GS_DATA_DIR', '/data/geodata')
GS_TMP_DIR = getattr(settings, 'GS_TMP_DIR', '/tmp')
RSYNC_WAIT_TIME = getattr(settings, 'RSYNC_WAIT_TIME', 0)

GPMOSAIC_COVERAGE_JSON = """{
    "coverage": {
        "enabled": true,
        "metadata": {
            "entry": [
                {
                    "@key": "time",
                    "dimensionInfo": {
                        "defaultValue": "",
                        "enabled": true,
                        "presentation": "LIST",
                        "units": "ISO8601"
                    }
                }
            ]
        }
    }
}"""

GPMOSAIC_DS_PROPERTIES = """SPI=org.geotools.data.postgis.PostgisNGDataStoreFactory
host=localhost
port=5432
database={db_data_instance}
schema=public
user={db_user}
passwd={db_password}
Loose\ bbox=true
Estimated\ extends=false
validate\ connections=true
Connection\ timeout=10
preparedStatements=true
"""

GPMOSAIC_TIME_REGEX = "regex=[0-9]{8}T[0-9]{9}Z"

GPMOSAIC_INDEXER_PROP = """TimeAttribute=ingestion
Schema=*the_geom:Polygon,location:String,ingestion:java.util.Date
PropertyCollectors=TimestampFileNameExtractorSPI[timeregex](ingestion)
"""


class GeoDataProcessor(object):
    """
    Base class to handle geodata retrieval and processing
    for import into GeoNode/GeoServer
    """

    gs_url = "http://{}:8080/geoserver/rest/workspaces/{}/coveragestores/{}/file.geotiff"
    gs_vec_url = "http://{}:8080/geoserver/rest/workspaces/{}/datastores/{}/featuretypes"
    gs_style_url = "http://{}:8080/geoserver/rest/styles/"

    def __init__(self, workspace=DEFAULT_WORKSPACE, tmp_dir=GS_TMP_DIR,
                 **kwargs):
        self.workspace = workspace
        self.tmp_dir = tmp_dir
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        if 'days' in kwargs.keys():
            self.days = kwargs['days']

    def download(self, url, filename=None):
        """
        Download a file from the specified URL
        :param url: The URL to download from
        :param filename: Optional name of the downloaded file.
        :return: Name of the downloaded file (not including path).
        """
        if not filename:
            filename = url.rsplit('/')[-1]
        r = requests.get(url, stream=True)
        with open(os.path.join(self.tmp_dir, filename), 'wb') as out_file:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    out_file.write(chunk)
                    out_file.flush()
        r.raise_for_status()
        return filename

    def truncate_gs_cache(self, layer_name):
        _user, _password = ogc_server_settings.credentials
        gwc_url = "{base_url}gwc/rest/seed/{ws}:{layer}.json".format(
            base_url=ogc_server_settings.LOCATION,
            ws=self.workspace,
            layer=layer_name
        )
        truncate_json = json.dumps({'seedRequest':
                                        {'name': 'geonode:{}'.format(
                                            layer_name),
                                         'srs': {'number': 900913},
                                         'zoomStart': 0,
                                         'zoomStop': 19,
                                         'format': 'image/png',
                                         'type': 'truncate',
                                         'threadCount': 4
                                         }
                                    })
        res = requests.post(url=gwc_url, data=truncate_json,
                            auth=(_user, _password),
                            headers={"Content-type": "application/json"})
        res.raise_for_status()

    def post_geoserver(self, tif_file, layer_name):
        """
        Upload a GeoTIFF to GeoServer as a coverage layer
        :param tif_file: Full path&name of GeoTIFF to import
        :param layer_name: Name of the coverage layer
        """
        # Post to Geoserver
        gs_url = self.gs_url.format(ogc_server_settings.hostname,
                                    self.workspace, layer_name)
        data = None
        with open(os.path.join(self.tmp_dir, tif_file), 'rb') as tif_binary:
            data = tif_binary.read()
        _user, _password = ogc_server_settings.credentials
        res = requests.put(url=gs_url,
                           data=data,
                           auth=(_user, _password),
                           headers={'Content-Type': 'image/tif'})

        res.raise_for_status()
        return res.content

    def post_geoserver_vector(self, layer_name,
                              store=ogc_server_settings.DATASTORE):
        """
        Add a PostGIS table into GeoServer as a layer
        :param layer_name:
        :return:
        """
        gs_url = self.gs_vec_url.format(ogc_server_settings.hostname,
                                        self.workspace, store)
        data = "<featureType><name>{}</name></featureType>".format(layer_name)
        _user, _password = ogc_server_settings.credentials
        res = requests.post(url=gs_url,
                            data=data,
                            auth=(_user, _password),
                            headers={'Content-Type': 'text/xml'})

        res.raise_for_status()
        return res.content

    def update_geonode(self, layer_name, title="", bounds=None):
        """
        Update a layer and it's title in GeoNode
        :param layer_name: Name of the layer
        :param title: New title for layer
        """
        # Update the layer in GeoNode
        ulc = UpdateLayersCommand()
        ulc.handle(verbosity=1, filter=layer_name)

        if title:
            from geonode.layers.models import Layer
            lyr = Layer.objects.get(typename='geonode:{}'.format(layer_name))
            lyr.title = title
            lyr.save()
            if bounds:
                from geonode.layers.models import Layer
                res = lyr.gs_resource
                res.native_bbox = bounds
                _user, _password = ogc_server_settings.credentials
                url = ogc_server_settings.rest
                gs_catalog = Catalog(url, _user, _password)
                gs_catalog.save(res)

    def set_default_style(self, layer_name, sld_name, sld_content):
        """
        Create a style and assign it as default to a layer
        :param layer_name: the layer to assign the style to
        :param sld_name: the name to give the style
        :param sld_content: the actual XML content for the style
        :return: None
        """
        gs_url = self.gs_style_url.format(ogc_server_settings.hostname)

        # Create the style
        data = "<style><name>{name}</name><filename>{name}.sld</filename></style>".format(
            name=sld_name)
        _user, _password = ogc_server_settings.credentials
        res = requests.post(url=gs_url,
                            data=data,
                            auth=(_user, _password),
                            headers={'Content-Type': 'text/xml'})

        res.raise_for_status()

        # Populate the style
        data = sld_content
        url = urljoin(gs_url, sld_name)
        print url
        res = requests.put(url=url,
                           data=data,
                           auth=(_user, _password),
                           headers={'Content-Type':
                                        'application/vnd.ogc.sld+xml'})

        res.raise_for_status()

        # Assign to the layer
        layer_typename = "{}%3A{}".format(DEFAULT_WORKSPACE, layer_name)
        data = '<layer><defaultStyle><name>{}</name></defaultStyle></layer>'.format(
            sld_name)
        url = urljoin(gs_url.replace("styles", "layers"), layer_typename)
        print url
        res = requests.put(
            url=url,
            data=data,
            auth=(_user, _password),
            headers={'Content-Type': 'text/xml'})

        res.raise_for_status()

    def cleanup(self):
        """
        Remove any files in the temp directory matching
        the processor class prefix
        """
        filelist = glob.glob("{}*.*".format(
            os.path.join(self.tmp_dir, self.prefix)))
        for f in filelist:
            os.remove(f)

    def run(self):
        raise NotImplementedError


class GeoDataMosaicProcessor(GeoDataProcessor):
    """
    Processor for handling raster mosaic data stores
    http://docs.geoserver.org/latest/en/user/tutorials/imagemosaic_timeseries/imagemosaic_timeseries.html
    http://geoserver.geo-solutions.it/multidim/en/rest/index.html
    """

    gs_url = "http://{}:8080/geoserver/rest/workspaces/{}/coveragestores/{}/external.imagemosaic"
    mosaic_url = gs_url.replace('external.imagemosaic',
                                'coverages/{}/index/granules')
    create_url = gs_url.replace('external.imagemosaic', 'file.imagemosaic')

    archive_hours = ("T12:00:00.000Z",)
    days_to_keep = 30
    data_dir = "{gsd}/data/{ws}/{layer}/{file}"
    local_gs = True

    def del_mosaic_image(self, url):
        """
        Remove an image from a mosaic store
        :param url: URL indicating which image from which mosaic to delete
        :return: response status and content
        """
        _user, _password = ogc_server_settings.credentials
        r = requests.delete(url, auth=(_user, _password))
        r.raise_for_status()
        return r.status_code, r.content

    def post_geoserver(self, filepath, layer_name):
        """
        Add another image to a mosaic datastore
        :param filepath: Full path&name of GeoTIFF to import
        :param layer_name: Name of the mosaic layer & store (assumed to be same)
        """
        sleep(RSYNC_WAIT_TIME)
        gs_url = self.gs_url.format(ogc_server_settings.hostname,
                                    self.workspace, layer_name)
        data = "file://{}".format(filepath)
        _user, _password = ogc_server_settings.credentials
        res = requests.post(url=gs_url,
                            data=data,
                            auth=(_user, _password),
                            headers={'Content-Type': 'text/plain'})
        if res.status_code == 405:
            logger.warn("Mosaic may not exist, try to create it")
            self.create_mosaic(layer_name, filepath)
        else:
            res.raise_for_status()

    def remove_mosaic_granules(self, mosaic_url, mosaic_query, layer_name):
        """
        Remove granules from an image mosaic based on query parameters
        :param mosaic_url: The base image mosaic REST URL
        :param mosaic_query: Query specifying which granules to remove
        :param layer_name: The name of the image mosaic layer
        :return: None
        """
        _user, _password = ogc_server_settings.credentials
        r = requests.get("{url}.json?filter={query}".format(
            url=mosaic_url, query=mosaic_query),
            auth=(_user, _password))
        r.raise_for_status()
        fc = json.loads(r.content)
        for feature in fc['features']:
            dst_file = self.data_dir.format(
                gsd=GS_DATA_DIR, ws=self.workspace,
                layer=layer_name, file=feature['properties']['location'])
            if os.path.isfile(dst_file):
                os.remove(dst_file)
            self.del_mosaic_image("{}/{}".format(mosaic_url, feature['id']))

    def drop_old_hourly_images(self, nowtime, layer_name):
        """
        Remove any of today's previous hourly images from the mosaic,
        except for the archive hour.
        :param nowtime: Current date/time
        :param layer_name: Geoserver mosaic store/layer name
        """
        today = nowtime.strftime("%Y-%m-%dT%H:00:00.000Z")
        morn = nowtime.strftime("%Y-%m-%dT00:00:00.000Z")
        archive_query = ""

        # Remove today's old images
        for hour in self.archive_hours:
            archive_query += (" AND ingestion<>" +
                              nowtime.strftime("%Y-%m-%d{}".format(hour)))
        mosaic_index_url = self.mosaic_url.format(ogc_server_settings.hostname,
                                                  self.workspace,
                                                  layer_name,
                                                  layer_name)
        mosaic_query = (
            "ingestion<{now} AND ingestion>={morn}{archive_query}".format(
                now=today, morn=morn, archive_query=archive_query))
        self.remove_mosaic_granules(mosaic_index_url, mosaic_query, layer_name)

        # Remove yesterday's old images if any remaining
        yesterday = nowtime - datetime.timedelta(days=1)
        archive_query = ""
        for hour in self.archive_hours:
            archive_query += (" AND ingestion<>" + yesterday.strftime(
                "%Y-%m-%d{}".format(hour)))
        mosaic_query = (
            "ingestion<{morn} AND ingestion>={yestermorn}{archive}".format(
                morn=morn,
                archive=archive_query,
                yestermorn=yesterday.strftime("%Y-%m-%dT00:00:00.000Z")))
        self.remove_mosaic_granules(mosaic_index_url, mosaic_query, layer_name)

    def drop_old_daily_images(self, nowtime, layer_name):
        """
        Remove any images from the mosaic older than the 'days_to_keep'
        property (default is 30).
        :param nowtime: Current date/time
        :param layer_name: Geoserver mosaic store/layer name
        """
        _user, _password = ogc_server_settings.credentials
        month_cutoff = (nowtime - datetime.timedelta(
            days=self.days_to_keep)).strftime("%Y-%m-%dT00:00:00.000Z")
        mosaic_index_url = self.mosaic_url.format(ogc_server_settings.hostname,
                                                  self.workspace,
                                                  layer_name,
                                                  layer_name)
        mosaic_query = "ingestion<={}".format(month_cutoff)
        self.remove_mosaic_granules(mosaic_index_url, mosaic_query, layer_name)

    def create_mosaic_properties_zip(self, layer_name, img_file):
        """
        Create a zipfile containing the required config files and
        seed image for a time-enabled raster mosaic datastore.
        :param layer_name: name of layer to create
        :param img_file: full path + name of seed image
        :return: full path+name of created zip file
        """
        tmp_dir = os.path.join(self.tmp_dir, layer_name)
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        zip_archive = os.path.join(tmp_dir, "props.zip")
        try:
            with ZipFile(zip_archive, 'w') as zipFile:
                zipFile.write(img_file, os.path.basename(img_file))

                dsprop_file = os.path.join(tmp_dir, 'datastore.properties')
                with open(dsprop_file, 'w') as datastore_prop:
                    db = ogc_server_settings.datastore_db
                    properties = GPMOSAIC_DS_PROPERTIES.format(
                        db_data_instance=db['NAME'],
                        db_user=db['USER'],
                        db_password=db['PASSWORD']
                    )
                    datastore_prop.write(properties)
                zipFile.write(dsprop_file, 'datastore.properties')

                trprop_file = os.path.join(tmp_dir, 'timeregex.properties')
                with open(trprop_file, 'w') as time_prop:
                    time_prop.write(GPMOSAIC_TIME_REGEX)
                zipFile.write(trprop_file, 'timeregex.properties')

                idxprop_file = os.path.join(tmp_dir, 'indexer.properties')
                with open(idxprop_file, 'w') as index_prop:
                    index_prop.write(GPMOSAIC_INDEXER_PROP)
                zipFile.write(idxprop_file, 'indexer.properties')
            return zip_archive
        except Exception as e:
            shutil.rmtree(tmp_dir)
            raise e

    def create_mosaic(self, layer_name, img_file):
        """
        Create a time-enabled image mosaic datastore and layer
        :param layer_name: Name of image mosaic layer/store to create
        :param img_file: Seed image for image mosaic
        :return: None
        """
        ziploc = self.create_mosaic_properties_zip(layer_name, img_file)
        gs_url = self.create_url.format(ogc_server_settings.hostname,
                                        self.workspace, layer_name)
        try:
            with open(ziploc, 'rb') as zipdata:
                data = zipdata.read()
                _user, _password = ogc_server_settings.credentials
                res = requests.put(url=gs_url,
                                   data=data,
                                   auth=(_user, _password),
                                   headers={'Content-Type': 'application/zip'})
                res.raise_for_status()
                gs_url = gs_url.replace(
                    'file.imagemosaic', 'coverages/{}.json'.format(layer_name))
                res = requests.put(url=gs_url,
                                   data=GPMOSAIC_COVERAGE_JSON,
                                   auth=(_user, _password),
                                   headers={'Content-Type': 'application/json'})
                res.raise_for_status()
        finally:
            if os.path.exists(ziploc):
                shutil.rmtree(os.path.dirname(ziploc))
