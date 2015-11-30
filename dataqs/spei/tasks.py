from __future__ import absolute_import

from celery import shared_task
from dataqs.spei.spei import SPEIProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def spei_task():
    processor = SPEIProcessor()
    processor.run()
