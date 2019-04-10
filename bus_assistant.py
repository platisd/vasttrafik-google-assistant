#!/usr/bin/python3
# -*- coding:utf8 -*-
"""
The Personal Bus Stop is the back-end for an Action on Google which utilizes
Google Assistant to fetch the upcoming trips from the station near my house
and my work.

This file acts as the gateway between the Python module which fetches the
upcoming bus or tram departures and the Google Assistant service.
"""

import json
from flask import Flask, request, make_response, jsonify
import departures
import weather_fetcher
import datetime

app = Flask("Personal-Bus-Stop")
# The currently supported stations we are interested in. The station id's are
# hardcoded and the id's can be discovered through the location API. E.g.:
# https://api.vasttrafik.se/bin/rest.exe/v2/location.name?input=almedal&format=json
home = departures.StationOfInterest(
    "Lindholmen", "9021014004490000", ['A', 'B'])
work = departures.StationOfInterest("Almedal", "9021014001050000", ['A'])
# We shouldn't make too many weather API calls or we wll start paying
previous_predictions = list()
previous_weather_api_call = datetime.datetime(1, 1, 1)


def respond_to_assistant(fullfilment):
    return make_response(jsonify({'fulfillmentText': fullfilment}))


def respond_to_info_center(station_a_departures, station_b_departures, predictions, current_time):
    response = {'depsA': station_a_departures, 'depsB': station_b_departures, 'pred': [
        (time, weather[:7], temperature) for time, weather, temperature in predictions], 'time': current_time}
    print(response)
    return make_response(jsonify(response))


def trips_to_response(location, trips):
    """
    Formulates a response to be read by Google Assistant

    location    The location where the trips depart from
    trips       The trips departing from the location of interest
    """
    # Sort the trip on departure order, first ones to leave first
    trips = sorted(trips, key=lambda trip: int(trip.minutes_left))
    response = "Departures from " + location + ":\n"
    for trip in trips:
        response += str(trip) + "\n"

    return response


@app.route('/departures', methods=['POST'])
def departures_handler():
    try:
        req = request.get_json(silent=True, force=True)
        print(json.dumps(req))

        location = req.get('queryResult').get(
            'parameters').get('current-location')

        vasttrafik = departures.init()  # Establish connection to Vasttrafik

        if location == 'home':
            stations_of_interest = [home]
        elif location == 'work':
            stations_of_interest = [work]
        else:
            return respond_to_assistant("I am not sure where " + location + " is.")

        trips = departures.get_next_trips(vasttrafik, stations_of_interest)

        return respond_to_assistant(trips_to_response(location, trips))
    except Exception as e:
        print(e)
        return respond_to_assistant("Sorry, an error occurred. Please check the server logs.")


@app.route('/info-center-data', methods=['GET'])
def info_center_handler():
    """ Gets data necessary to populate the Home Information Center
    """
    varbergsgatan = departures.StationOfInterest(
        "Varbergsgatan", "9021014007270000", ['A'])
    fredasgatan = departures.StationOfInterest(
        "Fredasgatan", "9021014012271000", ['B'])

    vasttrafik = departures.init()  # Establish connection to Vasttrafik
    trips_from_fredasgatan = departures.get_next_trips(vasttrafik, [
                                                       fredasgatan])
    trips_from_varbergsgatan = departures.get_next_trips(
        vasttrafik, [varbergsgatan])

    # Get the minutes to the next two departures for each station of interest
    departures_from_station_a = sorted([
        trip.minutes_left for trip in trips_from_varbergsgatan])
    departures_from_station_b = sorted([
        trip.minutes_left for trip in trips_from_fredasgatan])
    minutes_to_next_departures_from_station_a = [str(
        minutes_left) if minutes_left < 100 else "NA" for minutes_left in departures_from_station_a[:2]]
    minutes_to_next_departures_from_station_b = [str(
        minutes_left) if minutes_left < 100 else "NA" for minutes_left in departures_from_station_b[:2]]

    _, current_hours_minutes = departures.get_time()

    # Don't call the weather API too often not to exceed the usage limit
    global previous_weather_api_call, previous_predictions
    current_time = datetime.datetime.now()
    api_call_interval = 5 * 60
    if ((current_time - previous_weather_api_call).total_seconds() > api_call_interval):
        predictions = weather_fetcher.run()
        previous_weather_api_call = current_time
        previous_predictions = predictions
    else:
        predictions = previous_predictions

    return respond_to_info_center(minutes_to_next_departures_from_station_a, minutes_to_next_departures_from_station_b, predictions, current_hours_minutes)


def main():
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.run()


if __name__ == '__main__':
    main()
