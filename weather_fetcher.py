#!/usr/bin/python3
# -*- coding:utf8 -*-
import urllib.request
import os
import json
from datetime import datetime
from pytz import timezone


class WeatherPackage:
    def __init__(self, time, weather, temperature):
        self.time = time
        self.weather = weather
        self.temperature = temperature

    def __iter__(self):
        yield self.get_time()
        yield self.weather
        yield self.temperature

    def get_time(self):
        return datetime.fromtimestamp(self.time, timezone('Europe/Stockholm')).strftime("%H:%M")


def get_openweathermap_token(path_to_api_key):
    # Change working directory to the one that the file is residing in
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    # Parse the keys
    f = open(path_to_api_key)
    f.readline().replace('\n', "")
    f.readline().replace('\n', "")
    api_key = f.readline().replace('\n', "")
    f.close()
    return api_key


def get_forecast():
    return get_openweather_response("forecast")


def get_weather():
    return get_openweather_response("weather")


def get_openweather_response(endpoint):
    openweathermap_url = "https://api.openweathermap.org/data/2.5/%s?id=2711533&appid=%s&units=metric" % (
        endpoint, get_openweathermap_token("api-config"))
    response = urllib.request.urlopen(openweathermap_url)
    html_response = response.read()
    encoding = response.headers.get_content_charset('utf-8')
    decoded_html = html_response.decode(encoding)

    return json.loads(decoded_html)


def run():
    weather_json = get_weather()
    current_weather = weather_json['weather'][0]['main']
    current_temperature = weather_json['main']['temp']
    current_time = weather_json['dt']
    current_weather_package = WeatherPackage(
        current_time, current_weather, current_temperature)

    forecast_json = get_forecast()
    # Get weather data for up to the next 9 hours
    future_weather_packages = list()
    for i in range(0, 3):
        future_weather = forecast_json['list'][i]['weather'][0]['main']
        future_temperature = round(forecast_json['list'][i]['main']['temp'])
        future_time = forecast_json['list'][i]['dt']
        future_weather_packages.append(WeatherPackage(
            future_time, future_weather, future_temperature))

    return [current_weather_package] + future_weather_packages


if __name__ == '__main__':
    run()
