from __future__ import absolute_import
from celery import shared_task
from django.conf import settings
from dataqs.aqicn.aqicn import AQICNProcessor


@shared_task
def aqicn_task():
    processor = AQICNProcessor(countries=settings.AQICN_COUNTRIES or None)
    processor.run()


