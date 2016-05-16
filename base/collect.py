#!/usr/bin/python

import re
import pytz
from datetime import datetime

import base.collector.owm

from django.core.exceptions import ValidationError
from base.models import Forecast, Type, Location, Length


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

    reception_time = datetime.fromtimestamp(forecast['reception_time'], pytz.utc).astimezone(prague)
    prediction_time = datetime.fromtimestamp(forecast['prediction_time'], pytz.utc).astimezone(prague)

    # times are normalized to be properly recognized by other modules
    # due to how weatherlyzer is run, this should not be a problem
    reception_time = reception_time.replace(minute=0,second=0,microsecond=0)
    prediction_time = prediction_time.replace(minute=0,second=0,microsecond=0)

    # at the moment, only particular forecasts are used.
    if prediction_time != reception_time and reception_time.hour % 3 != 0:
        print("discarding forecast: future forecast's reception time: ", reception_time.hour, "%3 != 0")
        return

    # at the moment, only predictions for particular offsets are used.
    difference = prediction_time - reception_time
    difference_hours = difference.seconds // 60 // 60
    allowed_deltas = [x.length for x in Length.objects.all()]

    if difference_hours not in allowed_deltas:
        print("discarding forecast:",difference_hours, "not in", allowed_deltas)
        return

    # all type 'slugs' are saved if they are found in the forecast
    for value_type in Type.objects.all():
        if value_type.slug in forecast:
            Forecast.objects.create(
                location=place,
                forecasted_on=reception_time, 
                forecasting=prediction_time,
                value=forecast[value_type.slug],
                type=value_type
            )