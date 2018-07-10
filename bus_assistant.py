# !/usr/bin/env python
# -*- coding:utf8 -*-
"""
The Personal Bus Stop is an Action on Google which utilizes Google Assistant
to fetch the upcoming trips from the station near my house and my work.

This file acts as the gateway between the Python module which fetches the
upcoming bus or tram departures and the Google Assistant service.
"""

import json
from flask import Flask, request, make_response, jsonify
import departures

app = Flask("Personal-Bus-Stop")
# The currently supported stations we are interested in. The station id's are
# hardcoded and the id's can be discovered through the location API. E.g.:
# https://api.vasttrafik.se/bin/rest.exe/v2/location.name?input=almedal&format=json
home = departures.StationOfInterest("Lindholmen", "9021014004490000", ['A', 'B'])
work = departures.StationOfInterest("Almedal", "9021014001050000", ['A'])


def respond(fullfilment):
    return make_response(jsonify({'fulfillmentText': fullfilment}))


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

        location_data = req.get('queryResult').get('parameters').get('location')
        if 'shortcut' not in location_data:
            return respond("I do not know where this is.")

        location = location_data.get('shortcut')
        vasttrafik = departures.init()  # Establish connection to Vasttrafik

        if location == 'home':
            stations_of_interest = [home]
        elif location == 'work':
            stations_of_interest = [work]
        else:
            return respond("I am not sure where " + location + " is.")

        trips = departures.get_next_trips(vasttrafik, stations_of_interest)

        return respond(trips_to_response(location, trips))
    except Exception as e:
        print(e)
        return respond("Sorry, an error occurred. Please check the server logs.")


def main():
    app.run()


if __name__ == '__main__':
    main()
