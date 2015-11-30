from __future__ import absolute_import

from celery import shared_task
from dataqs.wqp.wqp import WaterQualityPortalProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def wqp_task():
    processor = WaterQualityPortalProcessor()
    processor.run()