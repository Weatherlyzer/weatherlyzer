
import pyowm

def get_forecasts(place):
  owm = pyowm.OWM("74878f953d3a8b89ee8e75ce4b5edd2a")
  weather_list = []

  # forecasts
  forecasts = owm.three_hours_forecast(place).get_forecast()
  reception_time = forecasts.get_reception_time()
  weather_list = [parse_weather(x,reception_time) for x in forecasts.get_weathers()]

  # current weather
  current = owm.weather_at_place(place)
  reception_time = current.get_reception_time()
  current = parse_weather(current.get_weather(),reception_time)
  current['reception_time'] = current['prediction_time']
  weather_list.append(current)
  
  return weather_list

def parse_weather(weather_object,reception_time):
  w = weather_object
  parsed_weather = {
    'temp': w.get_temperature(unit='celsius')['temp'],
    'pressure': w.get_pressure()['press'],
    'reception_time': reception_time,
    'prediction_time': w.get_reference_time(),
    'clouds': w.get_clouds(),
    'humidity': w.get_humidity(),
  }

  if 'speed' in w.get_wind():
    parsed_weather['wind_speed'] = w.get_wind()['speed']

  if '3h' in w.get_rain():
    parsed_weather['rain_3h'] = w.get_rain()['3h']

  return parsed_weather
