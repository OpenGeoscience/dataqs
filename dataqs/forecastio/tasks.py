from __future__ import absolute_import

from celery import shared_task
from dataqs.forecastio.forecastio_air import ForecastIOAirTempProcessor
from dataqs.helpers import single_instance_task


@shared_task
@single_instance_task
def forecast_io_task():
    processor = ForecastIOAirTempProcessor()
    processor.run()


