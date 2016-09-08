# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2012 OpenPlans
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Django settings for the GeoNode project.
from celery.schedules import crontab

# Append these to INSTALLED_APPS
DATAQS_APPS = (
    'dataqs',
    'dataqs.aqicn',
    'dataqs.airnow',
    'dataqs.forecastio',
    'dataqs.gdacs',
    'dataqs.gfms',
    'dataqs.nasa_gpm',
    'dataqs.spei',
    'dataqs.usgs_quakes',
    'dataqs.wqp',
    'dataqs.hifld',
    'dataqs.gistemp',
)

# CELERY SETTINGS
BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT = 'redis'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'redis://'
CELERY_ALWAYS_EAGER = False
CELERY_SEND_TASK_ERROR_EMAILS = True
CELERYD_POOL_RESTARTS = True
CELERY_ENABLE_REMOTE_CONTROL = True

# AirNow API username:password
# (sign up for a free account at http://airnowapi.org/account/request/)
AIRNOW_ACCOUNT = 'your_airnow_username:your_airnow_password'

# NASA GPM FTP ACCOUNT
# (sign up at http://registration.pps.eosdis.nasa.gov/registration/)
GPM_ACCOUNT = 'your_gpm_email_account'

# Location of GeoServer data directory
GS_DATA_DIR = '/var/lib/tomcat7/webapps/geoserver/data'

# Directory where temporary data_queues geoprocessing files should
# be downloaded
GS_TMP_DIR = '/tmp'

# Time to wait before updating Geoserver mosaic (keep at 0 unless Geoserver
# is on a different server.
# In that case, there will need to be an automated rsync between GS_TMP_DIR
# where celery is running and
# GS_DATA_DIR where GeoServer is running.
RSYNC_WAIT_TIME = 0

# Add more scheduled geoprocessors here (ideally in local_settings.py file)
CELERYBEAT_SCHEDULE = {
    'gfms': {
        'task': 'dataqs.gfms.tasks.gfms_task',
        'schedule': crontab(minute=3),
        'args': ()
    },
    'forecast_io': {
        'task': 'dataqs.forecastio.tasks.forecast_io_task',
        'schedule': crontab(minute=1),
        'args': ()
    },
    'aqicn': {
        'task': 'dataqs.aqicn.tasks.aqicn_task',
        'schedule': crontab(hour=5, minute=0),
        'args': ()
    },
    'gdacs': {
        'task': 'dataqs.gdacs.tasks.gdacs_task',
        'schedule': crontab(hour=1, minute=0),
        'args': ()
    },
    'usgs_quakes': {
        'task': 'dataqs.usgs_quakes.tasks.usgs_quake_task',
        'schedule': crontab(hour=3,  minute=0),
        'args': ()
    },
    'spei': {
        'task': 'dataqs.spei.tasks.spei_task',
        'schedule': crontab(hour=4, minute=0),
        'args': ()
    },
    'wqp': {
        'task': 'dataqs.wqp.tasks.wqp_task',
        'schedule': crontab(hour=2, minute=0),
        'args': ()
    },
    'airnow': {
        'task': 'dataqs.gfms.tasks.airnow_task',
        'schedule': crontab(hour=6, minute=0),
        'args': ()
    },
    'nasa_gpm': {
        'task': 'dataqs.nasa_gpm.tasks.nasa_gpm_task',
        'schedule': crontab(hour=7, minute=0),
        'args': ()
    },
    'hifld': {
        'task': 'dataqs.hifld.tasks.hifld_task',
        'schedule': crontab(day_of_week='sunday', hour=12, minute=0),
        'args': ()
    },
    'gistemp': {
        'task': 'dataqs.gistemp.tasks.gistemp_task',
        'schedule': crontab(day_of_month=15, hour=12, minute=0),
        'args': ()
    }
}

HIFLD_LAYERS = [
    {
        'name': 'US State Boundaries',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/718791120f6549708cb642dac6ff0dbf_0.geojson',
        'table': 'us_state_boundaries',
        'sld': 'polygon'
    },
    {
        'name': 'US County Boundaries',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/53270fe7036f428fbfb11c4511994a6f_0.geojson',
        'table': 'us_county_boundaries',
        'sld': 'polygon'
    },
    {
        'name': 'US Urban Areas',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/12076211b9f047aca1153cb079bbd923_0.geojson',
        'table': 'us_urban_areas',
        'sld': 'polygon'
    },
    {
        'name': 'Poultry Slaughtering and Processing Facilities ',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/b6b9cc72fb58476d92056d5c7ed25f8b_0.geojson',
        'table': 'poultry_facilities',
        'sld': 'point'
    },
    {
        'name': 'State Fairgrounds',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/7f35881c8860490ab6a76516978e9e15_0.geojson',
        'table': 'state_fairgrounds',
        'sld': 'point'
    },
    {
        'name': 'EPA Emergency Response (ER) Toxic Substances Control Act (TSCA) Facilities',
        'url': 'https://hifld-dhs-gii.opendata.arcgis.com/datasets/5e2d8818b8ca4dbc8f14ea2e118b9a86_0.geojson',
        'table': 'epa_tsca_facilities',
        'sld': 'point'
    }
]

def dataqs_extend():
    from settings import INSTALLED_APPS
    INSTALLED_APPS += DATAQS_APPS
