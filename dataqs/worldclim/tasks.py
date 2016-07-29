from __future__ import absolute_import

from celery import shared_task
from dataqs.worldclim.worldclim import WorldClimCurrentProcessor, \
    WorldClimPastProcessor, WorldClimFutureProcessor


@shared_task
def worldclim_current_task():
    processor = WorldClimCurrentProcessor()
    processor.run()


@shared_task
def worldclim_past_task():
    processor = WorldClimPastProcessor()
    processor.run()


@shared_task
def worldclim_future_task():
    processor = WorldClimFutureProcessor()
    processor.run()
