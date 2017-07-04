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
from db import create_db
from enum import Enum

from flask import Flask
from flask import request
from flask import make_response
from flask_sqlalchemy import SQLAlchemy

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    print("Result:")
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def parseDates(date_period):
    start, end = date_period.split('/')
    return [start, end]

class AnswerFormat(Enum):
    REVENUE = 1
    NUM_ORDERS = 2
    CUSTOMER_NAME = 3

def getAnswerFormat(customer_name, sort_by, queried_table):
    if customer_name:
        if sort_by == 'revenue':
            return AnswerFormat.REVENUE 
        if sort_by == 'number of orders':
            return AnswerFormat.NUM_ORDERS 
    elif queried_table == 'revenue':
        return AnswerFormat.REVENUE
    else:
        return AnswerFormat.CUSTOMER_NAME

def parametersToSql(queried_table, sort_by, k, size=None, date_period=None,
            customer_name=None):
    if customer_name:
        sql_base = '''
            SELECT {sort_by} FROM customer WHERE customer_name LIKE '%%{customer_name}%%'
        '''
        return sql_base.format(sort_by=sort_by, customer_name=customer_name)

    if size == 'top':
        sort_order = 'DESC'
    if size == 'smallest':
        sort_order = 'ASC'
    sql_base = '''
    SELECT customer_name FROM {queried_table} ORDER BY
    {sort_by} {sort_order} LIMIT {k}'''

    sql = sql_base.format(queried_table=queried_table,
                          sort_by=sort_by,
                          sort_order=sort_order,
                          k=k)
    if queried_table == 'revenue':
        if date_period:
          dates = parseDates(date_period)
          sql_base = '''
          SELECT SUM(revenue) FROM revenue
      WHERE STRCMP(date, "{date_period_start}") > 0 AND
        STRCMP(date, "{date_period_end}") < 0
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
    size = parameters.get("size") or 'top'
    k = parameters.get("number") or 1
    date_period = parameters.get("date-period")
    customer_name=parameters.get("Customer")


    if sort_by == 'number of orders':
      sort_by = 'orders'

    sql_to_run = parametersToSql(queried_table, sort_by, k,
                 size=size,
                 date_period=date_period,
                 customer_name=customer_name)

    

    print('sql_to_run: %s' % sql_to_run)
    res = db.engine.execute(sql_to_run)
    res_list = list(res)
    text = speech = ', '.join([str(a[0]) for a in res_list])
    answer_format = getAnswerFormat(customer_name, sort_by, queried_table)

    if answer_format == AnswerFormat.REVENUE:
        text = '$' + text
        revenue = int(speech)
        if revenue/1000000 > 1:
               rev_rounded = revenue / 100000
               rev_rounded = float(rev_rounded)/10
               speech = '$%d Million' % rev_rounded
        elif revenue/100000:
               rev_rounded = revenue / 1000
               speech = '$%d thousand' % rev_rounded
    response = {
        "speech": speech,
        "displayText": text,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
    print(response)
    return response

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

db = None

if __name__ == '__main__':
    app2, db = create_db(app)
    with app2.app_context():
        port = int(os.getenv('PORT', 8080))
    
        print("Starting app on port %d" % port)
        db = SQLAlchemy()

    app.run(debug=False, port=port, host='0.0.0.0')
