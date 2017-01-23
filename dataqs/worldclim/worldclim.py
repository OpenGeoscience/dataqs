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

import argparse
import calendar
import os
import shutil
from zipfile import ZipFile

import itertools

from requests import HTTPError

from dataqs.helpers import gdal_translate, style_exists
from dataqs.processor_base import GeoDataProcessor
from geonode.base.models import TopicCategory

script_dir = os.path.dirname(os.path.realpath(__file__))


class WorldClimProcessor(GeoDataProcessor):
    """
    Base class for WorldClim data processors
    """

    prefix = 'worldclim'
    version = '1_4'
    biovars = [
        'Annual Mean Temperature',
        'Mean Diurnal Range',
        'Isothermality',
        'Temperature Seasonality',
        'Max Temperature of Warmest Month',
        'Min Temperature of Coldest Month',
        'Temperature Annual Range',
        'Mean Temperature of Wettest Quarter',
        'Mean Temperature of Driest Quarter',
        'Mean Temperature of Warmest Quarter',
        'Mean Temperature of Coldest Quarter',
        'Annual Precipitation',
        'Precipitation of Wettest Month',
        'Precipitation of Driest Month',
        'Precipitation Seasonality',
        'Precipitation of Wettest Quarter',
        'Precipitation of Driest Quarter',
        'Precipitation of Warmest Quarter',
        'Precipitation of Coldest Quarter'
    ]

    gcms = [
        ('bc', 'BCC-CSM1-1'),
        ('cc', 'CCSM4'),
        ('ce', 'CESM1-CAM5-1-FV2'),
        ('cn', 'CNRM-CM5'),
        ('hd', 'HadGEM2-AO'),
        ('hg', 'HadGEM2-CC'),
        ('he', 'HadGEM2-ES'),
        ('ip', 'IPSL-CM5A-LR'),
        ('mr', 'MIROC-ESM'),
        ('mp', 'MPI-ESM-LR'),
        ('mg', 'MRI-CGCM3')
    ]

    climate_vars = [
        ('tn', 'Minimum Temperature'),
        ('tx', 'Maximum Temperature'),
        ('pr', 'Precipitation'),
        ('bi', biovars)
    ]

    resolutions = ['10m', '5m', '2-5m']

    base_description = """WorldClim data layers were generated through
interpolation of average monthly climate data from weather stations on a 30
arc-second resolution grid (often referred to as "1 km2" resolution).
\n\nMethods: http://worldclim.org/methods1
\n\nSource: http://worldclim.org/version1
\n\nCitation: Hijmans, R.J., S.E. Cameron, J.L. Parra, P.G. Jones and A. Jarvis,
 2005. Very high resolution interpolated climate surfaces for global land areas.
 International Journal of Climatology 25: 1965-1978."""

    def custom_title(self, var_tuple, index):
        """
        Create a layer title
        :param var_tuple: tuple(variable initial, title prefix)
        :param index: number of month or bioclimate variable index
        :return: title
        """
        if var_tuple[0].startswith('bi'):
            return self.biovars[index - 1]
        else:
            return '{}:{}'.format(var_tuple[1], calendar.month_name[index])

    def publish(self, tif, name, title, desc):
        """
        Publish to Geoserver and Geonode
        :param tif: File path/name of TIF image
        :param name: layer name
        :param title: layer title
        :param desc: layer description
        :return: None
        """
        category = TopicCategory.objects.get(
            identifier='climatologyMeteorologyAtmosphere')

        if "Diurnal" in title:
            style = "worldclim_diurnal"
        elif "Isotherm" in title:
            style = "worldclim_isotherm"
        elif "Temperature" in title:
            if "Seasonality" in title:
                style = "worldclim_temp_seasonality"
            else:
                style = "worldclim_temp"
        elif "Precipitation" in title:
            if "Annual" in title:
                style = "worldclim_precip_annual"
            elif "Seasonality" in title:
                style = "worldclim_precip_seasonality"
            else:
                style = "worldclim_precip"
        else:
            style = "worldclim_bio"

        self.post_geoserver(tif, name)
        with open(os.path.join(
                script_dir, 'resources/{}.sld'.format(style))) as sld:
            self.set_default_style(name, style, sld.read(),
                                   create=not style_exists(style))
        self.truncate_gs_cache(name)
        self.update_geonode(
            name, title,
            description=desc, category=category, store=name,
            extra_keywords=['category:Climatology Meteorology'])

    def cleanup(self, outdir):
        """
        Clean up all downloaded files and unzipped folders
        :param outdir: Folder containing unzipped files
        :return: None
        """
        super(WorldClimProcessor, self).cleanup()
        shutil.rmtree(outdir, ignore_errors=True)


class WorldClimCurrentProcessor(WorldClimProcessor):
    """
    Class for processing 'current' data from the SPEI Global Drought Monitor
    (http://sac.csic.es/spei/map/maps.html)
    """

    climate_vars = [
        ('tmin', 'Minimum Temperature'),
        ('tmax', 'Maximum Temperature'),
        ('tmean', 'Mean Temperature'),
        ('prec', 'Precipitation'),
        ('bio', WorldClimProcessor.biovars)
    ]

    future_years = [2050, 2070]
    rcps = [26, 45, 60, 85]
    past_ages = [
        ('mid', 'Mid Holocene'),
        ('lgm', 'Last Glacial Maximum')
    ]

    base_url = 'http://biogeo.ucdavis.edu/data/climate/worldclim/' + \
               '{}/grid/cur/{}_{}_bil.zip'
    desc = """Interpolations of observed data for {},
    representative of 1960-1990.\n"""

    def process(self):

        for var in self.climate_vars:
            for res in self.resolutions:
                outdir = os.path.join(
                    self.tmp_dir, self.prefix, 'current', var[0], res)
                dl_zips = [[var][0][0]]
                if res == '30s' and [var][0][0] == 'bio':
                    dl_zips = ['bio1-9', 'bio10-19']
                for dl in dl_zips:
                    dl_name = "{}_{}_{}_{}.zip".format(self.prefix, "current",
                                                       dl, res)
                    if not os.path.exists(os.path.join(self.tmp_dir, dl_name)):
                        self.download(self.base_url.format(
                            self.version, dl, res), dl_name)
                try:
                    ZipFile(os.path.join(
                        self.tmp_dir, dl_name)).extractall(path=outdir)
                    layer_name = \
                        "WorldClim current conditions: {var}, {res} resolution"

                    varcount = 20 if var[0] == 'bio' else 13
                    var_iterator = range(1, varcount)

                    for v in var_iterator:
                        name = '{}_cur_{}{}_{}'.format(
                            self.prefix, var[0], v, res)
                        bil = os.path.join(
                            outdir, '{}{}.bil'.format(var[0], v))
                        tif = bil.replace('.bil', '.tif')
                        gdal_translate(bil,
                                       tif,
                                       projection='EPSG:4326',
                                       options=['COMPRESS=DEFLATE'])
                        title = layer_name.format(
                            var=self.custom_title(var, v),
                            res=res.replace('-', '.'))
                        desc = (self.base_description + self.desc).format(
                            self.custom_title(var, v)
                        )
                        self.publish(tif, name, title, desc)
                finally:
                    self.cleanup(outdir)


class WorldClimPastProcessor(WorldClimProcessor):
    """
    Class for processing 'past' data from the SPEI Global Drought Monitor
    (http://sac.csic.es/spei/map/maps.html)
    """

    base_url = 'http://biogeo.ucdavis.edu/data/climate/cmip5/' + \
        '{age}/{gcm}{age}{var}_{res}.zip'
    desc = """
Downscaled climate data from simulations with Global Climate Models for the {}
period, based on the {} global climate model, at {} resolution.
"""

    past_ages = [
        ('mid', 'Mid Holocene'),
        ('lgm', 'Last Glacial Maximum')
    ]

    def process(self):
        for var, res, age, gcm in itertools.product(
                self.climate_vars,
                self.resolutions,
                self.past_ages,
                self.gcms):
            outdir = os.path.join(
                self.tmp_dir, self.prefix, 'past', var[0], res)
            dl_name = "{}_{}_{}_{}_{}.zip".format(
                self.prefix, gcm[0], age[0], var[0], res)
            print dl_name
            if not os.path.exists(os.path.join(self.tmp_dir, dl_name)):
                try:
                    self.download(self.base_url.format(
                        self.version, age=age[0], gcm=gcm[0], res=res,
                        var=var[0]).lower(), dl_name)
                except HTTPError:
                    continue
            try:
                ZipFile(os.path.join(
                    self.tmp_dir, dl_name)).extractall(path=outdir)
                layer_name = "WorldClim {age} conditions w/{gcm} GCM: " + \
                             "{var}, {res} resolution"
                varcount = 20 if var[0] == 'bi' else 13
                var_iterator = range(1, varcount)

                for v in var_iterator:
                    name = '{}_{}_{}_{}{}_{}'.format(
                        self.prefix, age[0], gcm[0], var[0],
                        v, res)
                    original_tif = os.path.join(
                        outdir, '{}{}{}{}.tif'.format(
                            gcm[0], age[0], var[0], v))
                    tif = original_tif.replace('.tif', '_4326.tif')
                    gdal_translate(original_tif,
                                   tif,
                                   projection='EPSG:4326',
                                   options=['COMPRESS=DEFLATE'])
                    title = layer_name.format(
                        age=age[1],
                        gcm=gcm[1],
                        var=self.custom_title(var, v),
                        res=res.replace('-', '.'))
                    desc = (self.base_description + self.desc).format(
                        age[1], gcm[1], res.replace('-', '.')
                    )
                    self.publish(tif, name, title, desc)
            finally:
                self.cleanup(outdir)


class WorldClimFutureProcessor(WorldClimProcessor):
    """
    Class for processing 'future' data from the SPEI Global Drought Monitor
    (http://sac.csic.es/spei/map/maps.html)
    """

    gcms = WorldClimProcessor.gcms + [
        ('ac', 'ACCESS1-0 '),
        ('gf', 'GFDL-CM3'),
        ('gd', 'GFDL-ESM2G'),
        ('gs', 'GISS-E2-R'),
        ('in', 'INMCM4'),
        ('mi', 'MIROC-ESM-CHEM'),
        ('mc', 'MIROC5'),
        ('no', 'NorESM1-M')
    ]

    base_url = 'http://biogeo.ucdavis.edu/data/climate/cmip5/' + \
               '{res}/{gcm}{rcp}{var}{yr}.zip'
    desc = """
    Downscaled and calibrated climate projection data from simulations of the
{gcm} global climate model for the year {yr} with a Representative Concentration
Pathway of {rcp}, at {res} resolution."""

    rcps = [26, 45, 60, 85]
    years = [2050, 2070]

    def process(self):
        for var, res, rcp, year, gcm in itertools.product(
                self.climate_vars,
                self.resolutions,
                self.rcps,
                self.years,
                self.gcms):
            outdir = os.path.join(
                self.tmp_dir, self.prefix, 'future', var[0], res)
            dl_name = "{}_{}_{}_{}_{}_{}.zip".format(
                self.prefix, gcm[0], rcp, var[0], year, res)
            print dl_name
            if not os.path.exists(os.path.join(self.tmp_dir, dl_name)):
                try:
                    self.download(self.base_url.format(
                        rcp=rcp, gcm=gcm[0], res=res, yr=str(year)[2:],
                        var=var[0]), dl_name)
                except HTTPError:
                    continue
            try:
                ZipFile(os.path.join(
                    self.tmp_dir, dl_name)).extractall(path=outdir)
                layer_name = "WorldClim {rcp} conditions w/{gcm} GCM for " + \
                             "{yr} at RCP {rcp}: {var}, {res} resolution"
                varcount = 20 if var[0] == 'bi' else 13
                var_iterator = range(1, varcount)
                for v in var_iterator:
                    name = '{}_{}_{}_{}{}_{}_{}'.format(
                        self.prefix, rcp, gcm[0], var[0],
                        v, year, res)
                    original_tif = os.path.join(
                        outdir, '{}{}{}{}{}.tif'.format(
                            gcm[0], rcp, var[0], str(year)[2:], v))
                    tif = original_tif.replace('.tif', '_4326.tif')
                    gdal_translate(original_tif,
                                   tif,
                                   projection='EPSG:4326',
                                   options=['COMPRESS=DEFLATE'])
                    title = layer_name.format(
                        rcp=float(rcp/10),
                        gcm=gcm[1],
                        var=self.custom_title(var, v),
                        yr=year,
                        res=res.replace('-', '.'))
                    desc = (self.base_description + self.desc).format(
                        rcp=float(rcp/10), gcm=gcm[1], yr=year,
                        res=res.replace('-', '.')
                    )
                    self.publish(tif, name, title, desc)
            finally:
                self.cleanup(outdir)

if __name__ == '__main__':
    """
    Run one of the WorldClim processors (current, past, or future).
    Optionally specify resolutions (default is: 10m, 5m, 2.5m)
    """

    processors = {
        'current': WorldClimCurrentProcessor,
        'past': WorldClimPastProcessor,
        'future': WorldClimFutureProcessor
    }

    parser = argparse.ArgumentParser(description='Run a worldclim importer')
    parser.add_argument('-p', dest='processor', default='current',
                        help='Processor to run (current, past, future)')
    parser.add_argument(
        '-r', action='store', dest='resolutions',
        default='10m,5m,2-5m',
        help='Comma-delimited list of resolutions (10m,5m,2-5m, and/or 30s)')
    parser.add_argument(
        '-v', action='store', dest='variables', default=None,
        help='Comma-delimited list of variables (ex: tmin,tmax,bio)')

    args = parser.parse_args()
    pr = processors[args.processor]()
    pr.resolutions = args.resolutions.split(',')
    if args.variables:
        vars = args.variables.split(',')
        allvars = [item for item in pr.climate_vars]
        for item in allvars:
            if item[0] not in vars:
                pr.climate_vars.remove(item)
    pr.process()
