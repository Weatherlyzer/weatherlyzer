#!/usr/bin/python

import re
import pytz
from datetime import datetime

import base.collector.owm

from django.core.exceptions import ValidationError
from base.models import Forecast, Type, Location


# get_forecasts from specified collector and places
# returns list of weather forecasts (dictionaries with specific keys)
def get_forecasts(collector, places):
    forecasts = []

    for p in places:
        forecasts.extend(collector.get_forecasts(place))

    for f in forecasts:
        f['collector'] = x.__name__

    for f in forecasts:
        verify(f)

    return forecasts


def collect():
    # ... could load collector names from models once they are implemented
    collectors = [base.collector.owm]

    # loop through places
    for place in Location.objects.all():

        # look through collectors
        for c in collectors:

            # forecasts is a list of forecasts stored in a form of dictionary
            forecasts = c.get_forecasts(place.name)

            # add collector's name to every forecast
            for f in forecasts:
                f['collector'] = c.__name__

            # verify and save every forecast
            for f in forecasts:
                verify(f)
                save(f, place)

    print("done")


# verify that values in a (forecast) dictionary only contain allowed characters
def verify(forecast):
    pattern = "^[a-zA-Z0-9\-\.\,:\+\ ]+$"
    checker = re.compile(pattern)

    for k in forecast:
        if not bool(checker.match(str(forecast[k]))):
            raise ValidationError(forecast['collector'] + " contains invalid data: " + str(forecast[k]))


# use django models to save forecast dictionary
def save(forecast, place):
    prague = pytz.timezone('Europe/Prague')

    l = place
    r = reception_time = datetime.fromtimestamp(forecast['reception_time'], pytz.utc).astimezone(prague)
    p = prediction_time = datetime.fromtimestamp(forecast['prediction_time'], pytz.utc).astimezone(prague)

    keys = [
        'temp',
        'pressure',
        'clouds',
        'humidity',
        'speed',
        'rain_3h',
    ]

    for k in keys:
        if k in forecast:
            value_type = Type.objects.get_or_create(slug=k)[0]
            Forecast.objects.create(location=l, forecasted_on=r, forecasting=p, value=forecast[k], type=value_type)
