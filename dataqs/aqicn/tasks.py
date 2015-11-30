from __future__ import absolute_import
from celery import shared_task
from dataqs.aqicn.aqicn import AQICNProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def aqicn_task(countries):
    processor = AQICNProcessor(countries=countries)
    processor.run()


