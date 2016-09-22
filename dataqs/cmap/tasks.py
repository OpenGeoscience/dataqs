from __future__ import absolute_import

from celery import shared_task
from dataqs.cmap.cmap import CMAPProcessor


@shared_task
def cmap_task():
    processor = CMAPProcessor()
    processor.run()
