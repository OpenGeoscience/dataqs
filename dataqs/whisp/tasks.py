from __future__ import absolute_import

from celery import shared_task
from dataqs.whisp.whisp import WhispProcessor


@shared_task
def wqp_task():
    processor = WhispProcessor()
    processor.run()
