from __future__ import absolute_import

from celery import shared_task
from dataqs.airnow.airnow import AirNowGRIB2HourlyProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def airnow_grib_hourly_task():
    processor = AirNowGRIB2HourlyProcessor()
    processor.run()
