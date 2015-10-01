from __future__ import absolute_import

from celery import shared_task
from dataqs.wqp.wqp import WaterQualityPortalProcessor


@shared_task
def airnow_grib_hourly_task():
    processor = WaterQualityPortalProcessor()
    processor.run()