from __future__ import absolute_import

from celery import shared_task
from dataqs.airnow.airnow import AirNowGRIB2HourlyProcessor


@shared_task
def airnow_grib_hourly_task():
    processor = AirNowGRIB2HourlyProcessor()
    processor.run()
