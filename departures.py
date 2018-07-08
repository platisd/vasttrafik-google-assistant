#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
VasttraPi - Your personal departures screen for Västtrafik buses

Running on: 2017-03-02-raspbian-jessie
To run the python GUI on startup appended python3 /home/pi/vasttraPi/departures.py in /home/pi/.xsession

PEP8 check with: pep8 --ignore=E501 departures.py
"""
import pytrafik.client
import json
from datetime import datetime
from pytz import timezone
import os
from datetime import datetime
from collections import defaultdict


class StationOfInterest:
    def __init__(self, station_name, station_id, tracks):
        self.name = station_name
        self.id = station_id
        self.tracks = tracks


class Trip:
    def __init__(self, vehicle_type, line, destination, minutes_left):
        self.vehicle_type = vehicle_type.capitalize()
        self.line = line
        self.destination = destination
        self.minutes_left = int(minutes_left)

    def __repr__(self):
        return self.vehicle_type + " " + self.line + " towards " + self.destination + " departs in " + str(self.minutes_left) + " minutes."


def init_vasttrafik_api_keys(path_to_api_keys):
    """
    Fetches the consumer and secret key from a relative path to a configuration
    file which should not be version controlled. The first line is the key and
    the second is the secret.

    Returns a tuple as (api_key, api_secret)
    """
    # Change working directory to the one that the file is residing in
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    # Parse the keys
    f = open(path_to_api_keys)
    api_key = f.readline().replace('\n', "")
    api_secret = f.readline().replace('\n', "")
    f.close()
    return (api_key, api_secret)


def init_connection(api_key, api_secret):
    """
    Initializes the connection to the Vasttrafik server

    Returns Vasttrafik connection or None if connection failed
    """
    try:
        return pytrafik.client.Client("json", api_key, api_secret)
    except Exception as e:
        print(e)
        print("Authentication failure!")
        return None


def get_time():
    """
    Fetches the local time in Gothenburg

    Returns a tuple with the current date and time
    """
    sweden = timezone('Europe/Stockholm')
    se_time = datetime.now(sweden)

    return (se_time.strftime("%Y-%m-%d"), se_time.strftime("%H:%M"))


def get_next_trips(vasttrafik, stations):
    """
    Fetches the next bus or tram trips for the specified list of
    StationOfInterest and connection to the Vasttrafik servers.

    Returns A list of bus/tram line numbers and minutes to depart for the next
            two trips of each bus or tram line.
    """
    # Get the current time and date from an NTP server as the host might not have an RTC
    (current_date, current_time) = get_time()
    trips = defaultdict(list)  # A dictionary of lists, holding a list of departures for each bus
    for station in stations:
        # Get the departures for each station we are interested in
        try:
            departures = vasttrafik.get_departures(station.id, date=current_date, time=current_time)
        except Exception as e:
            print("Connection failure for station %s" % station.name)
            departures = []  # If something went wrong, empty the departures list so we don't try to iterate through them
        for departure in departures:
            if departure['track'] in station.tracks:
                try:
                    # Sometimes rtTime is not returned, so fall back to normal time instead
                    departure_time = departure['rtTime'] if 'rtTime' in departure else departure['time']
                    trips[(departure['sname'], departure['direction'], departure['type'])].append(departure_time)
                except Exception as e:
                    print("Error while parsing server response")

    nextTrips = []
    for (line, destination, vehicle_type), departure_times in trips.items():
            remaining_departures = 2  # The number of departures that we care to show
            for departure_time in departure_times:
                remaining_departures -= 1
                if remaining_departures < 0:
                    break
                minutes_to_leave = ((datetime.strptime(departure_time, "%H:%M") - datetime.strptime(current_time, "%H:%M")).total_seconds() / 60)
                # If a bus leaves the next day, the above result will be a negative number, therefore we need to completement it
                # with the amount of minutes in a day (1440)
                if minutes_to_leave < 0:  # meaning that the next departure time is on the next day
                    MINUTES_IN_DAY = 1440
                    minutes_to_leave += MINUTES_IN_DAY
                nextTrips.append(Trip(vehicle_type, line, destination, minutes_to_leave))

    return nextTrips


def init():
    """
    Initialize the connection to the server and get a Vasttrafik connection
    object back.

    Returns a Vasttrafik object upon a successful connection, None otherwise
    """
    # Initialize the API keys using the local config file `api-config`
    (api_key, api_secret) = init_vasttrafik_api_keys("api-config")

    return init_connection(api_key, api_secret)
