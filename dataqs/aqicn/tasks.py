from __future__ import absolute_import
from celery import shared_task
from dataqs.aqicn.aqicn import AQICNProcessor


@shared_task
def aqicn_task(countries):
    processor = AQICNProcessor(countries=countries)
    processor.run()
