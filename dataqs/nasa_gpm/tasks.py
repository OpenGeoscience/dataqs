from __future__ import absolute_import

from celery import shared_task
from .nasa_gpm import GPMProcessor


@shared_task
def nasa_gpm_task():
    processor = GPMProcessor()
    processor.run()
