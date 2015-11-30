from __future__ import absolute_import

from celery import shared_task
from dataqs.gfms.gfms import GFMSProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def gfms_task():
    processor = GFMSProcessor()
    processor.run()
