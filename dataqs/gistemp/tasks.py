from __future__ import absolute_import

from celery import shared_task
from dataqs.gistemp.gistemp import GISTEMPProcessor


@shared_task
def gistemp_task():
    processor = GISTEMPProcessor()
    processor.run()
