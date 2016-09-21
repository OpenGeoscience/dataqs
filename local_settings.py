from django.conf import settings

INSTALLED_APPS = settings.INSTALLED_APPS + (
  'dataqs',
  'dataqs.aqicn',
  'dataqs.airnow',
  'dataqs.forecastio',
  'dataqs.gfms',
  'dataqs.gdacs',
  'dataqs.nasa_gpm',
  'dataqs.spei',
  'dataqs.usgs_quakes',
  'dataqs.gistemp',
  'dataqs.worldclim',
)
