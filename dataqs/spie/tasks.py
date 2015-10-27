from __future__ import absolute_import

from celery import shared_task
from .spie import SPIEProcessor

@shared_task
def spei_task():
    processor = SPIEProcessor()
    processor.run()
