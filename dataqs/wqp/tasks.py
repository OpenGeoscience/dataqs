from __future__ import absolute_import

from celery import shared_task
from dataqs.wqp.wqp import WaterQualityPortalProcessor


@shared_task
def wqp_task():
    processor = WaterQualityPortalProcessor()
    processor.run()