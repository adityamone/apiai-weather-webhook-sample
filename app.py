#!/usr/bin/env python

from __future__ import print_function
#from future.standard_library import install_aliases
#install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

import hard_coded_request

from flask import Flask
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def parseDates(date_period):
    start, end = date_period.split('/')
    return [start, end]

def parametersToSql(queried_table, sort_by, k, date_period=None):
    sql_base = '''
    SELECT customer_name FROM {queried_table} ORDER BY
    {sort_by} DESC LIMIT {k}'''

    sql = sql_base.format(queried_table=queried_table,
                          sort_by=sort_by,
                          k=k)
    if queried_table == 'revenue':
        if date_period:
          dates = parseDates(date_period)
          sql_base = '''
          SELECT SUM(billed_amount) FROM order
          WHERE order_date > "{date_period_start}" AND
                order_date < "{date_period_end}"
          '''
          sql = sql_base.format(date_period_start=dates[0],
                                date_period_end=dates[1])
        else:
          sql = '''
          SELECT SUM(billed_amount) FROM order
          '''

    return sql

def processRequest(req):
    parameters = req.get("result").get("parameters")
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    queried_table = parameters.get("queried_table") or 'customer'
    sort_by = parameters.get("sort_by") or 'revenue'
    k = parameters.get("number") or 1
    date_period = parameters.get("date-period")

    if sort_by == 'number of orders':
      sort_by = 'orders'

    sql_to_run = parametersToSql(queried_table, sort_by, k,
                                 date_period=date_period)
    print(sql_to_run)

    return {
        "speech": sql_to_run,
        "displayText": sql_to_run,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
    #baseurl = "https://query.yahooapis.com/v1/public/yql?"
    #yql_query = makeYqlQuery(req)
    #if yql_query is None:
    #    return {}
    #yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    #result = urlopen(yql_url).read()
    #data = json.loads(result)
    #res = makeWebhookResult(data)
    #return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)
    processRequest(json.loads(hard_coded_request.THREE_BIGGEST))
    db = SQLAlchemy()

    app.run(debug=False, port=port, host='0.0.0.0')
