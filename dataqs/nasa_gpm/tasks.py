from __future__ import absolute_import

from celery import shared_task
from dataqs.nasa_gpm.nasa_gpm import GPMProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def nasa_gpm_task():
    processor = GPMProcessor()
    processor.run()
