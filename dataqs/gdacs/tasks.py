from __future__ import absolute_import

from celery import shared_task
from .gdacs import GDACSProcessor

@shared_task()
def gdacs_task():
    processor = GDACSProcessor()
    processor.run()
