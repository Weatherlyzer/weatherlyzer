
import pyowm

def get_forecasts(place):
  owm = pyowm.OWM("74878f953d3a8b89ee8e75ce4b5edd2a")

  forecasts = owm.three_hours_forecast(place).get_forecast()

  reception_time = forecasts.get_reception_time()

  forecasts = [parse_weather(x,reception_time) for x in forecasts.get_weathers()]

  return forecasts

def parse_weather(w,reception_time):
  c = {
    'temp': w.get_temperature(unit='celsius')['temp'],
    'pressure': w.get_pressure()['press'],
    'reception_time': reception_time,
    'prediction_time': w.get_reference_time(),
    'clouds': w.get_clouds(),
    'humidity': w.get_humidity(),
  }

  if 'speed' in w.get_wind():
    c['wind_speed'] = w.get_wind()['speed']

  if '3h' in w.get_rain():
    c['rain_3h'] = w.get_rain()['3h']

  return c