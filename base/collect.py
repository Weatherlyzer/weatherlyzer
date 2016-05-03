#!/usr/bin/python

import re
from datetime import datetime

import base.collector.owm

from django.core.exceptions import ValidationError
from base.models import Forecast, Type, Location

# get_forecasts from specified collector and places
# returns list of weather forecasts (dictionaries with specific keys)
def get_forecasts(collector,places):

  weather_list = []

  for p in places:
    weather_list.extend(collector.get_forecasts(place))

  for w in weather_list:
    w['collector'] = x.__name__

  for w in weather_list:
    verify(w)
  
  return weather_list


def collect():

  #... could load collector names from models once they are implemented
  collectors = [base.collector.owm]
  
  # loop through places
  for place in Location.objects.all():

    # look through collectors
    for c in collectors:

      # l is a list of forecasts stored in a form of dictionary
      l = c.get_forecasts(place.name)

      # add collector's name to every forecast
      for d in l:
        d['collector'] = c.__name__

      # verify and save every forecast
      for forecast in l:
        verify(forecast)
        save(forecast,place)

  print("done")


# verify that values in a (forecast) dictionary only contain allowed characters
def verify(d):
  pattern = "^[a-zA-Z0-9\-\.\,:\+\ ]+$"
  checker = re.compile(pattern)

  for k in d:
    if not bool(checker.match(str(d[k]))):
      raise ValidationError(d['collector'] + " contains invalid data: " + str(d[k]))

# use django models to save forecast dictionary
def save(d,place):
  l = place
  r = reception_time = datetime.fromtimestamp(d['reception_time'])
  p = prediction_time = datetime.fromtimestamp(d['prediction_time'])

  keys = [
    'temp',
    'pressure',
    'clouds',
    'humidity',
    'speed',
    'rain_3h',
  ]

  for k in keys:
    if k in d:
      value_type = Type.objects.get_or_create(slug=k)[0]
      Forecast.objects.create(location=l,forecasted_on=r,forecasting=p,value=d['temp'],type=value_type)


