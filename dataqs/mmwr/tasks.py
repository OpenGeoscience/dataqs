from __future__ import absolute_import

from celery import shared_task
from dataqs.mmwr.mmwr import MortalityProcessor


@shared_task()
def mmwr_task():
    processor = MortalityProcessor()
    processor.run()
