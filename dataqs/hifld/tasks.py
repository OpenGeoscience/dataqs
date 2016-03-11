from __future__ import absolute_import
from celery import shared_task
from dataqs.hifld.hifld import HIFLDProcessor


@shared_task
def hifld_task():
    processor = HIFLDProcessor()
    processor.run()
