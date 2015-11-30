from __future__ import absolute_import

from celery import shared_task
from dataqs.gdacs.gdacs import GDACSProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def gdacs_task():
    processor = GDACSProcessor()
    processor.run()
