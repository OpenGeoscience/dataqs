from __future__ import absolute_import

from celery import shared_task
from dataqs.usgs_quakes.usgs_quakes import USGSQuakeProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def usgs_quake_task():
    processor = USGSQuakeProcessor()
    processor.run()
