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

app = Flask("Personal-Bus-Stop")


def respond(fullfilment):
    return make_response(jsonify({'fulfillmentText': fullfilment}))


@app.route('/departures', methods=['POST'])
def webhook():
    try:
        req = request.get_json(silent=True, force=True)

        print(json.dumps(req))

        location_data = req.get('queryResult').get('parameters').get('location')
        if 'shortcut' not in location_data:
            return respond("I do not know where this is.")

        location = location_data.get('shortcut')

        if location == 'home':
            res = "No place like home"
        elif location == 'work':
            res = "Your work is cool"
        else:
            res = "I am not sure where " + location + " is."

        return respond(res)

    except Exception as e:
        print(e)
        return respond("Sorry, an error occurred. Please check the server logs.")


def main():
    app.run()


if __name__ == '__main__':
    main()
