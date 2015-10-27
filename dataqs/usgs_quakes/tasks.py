from __future__ import absolute_import

from celery import shared_task
from .usgs_quakes import USGSQuakeProcessor

@shared_task
def usgs_quake_task():
    processor = USGSQuakeProcessor()
    processor.run()
