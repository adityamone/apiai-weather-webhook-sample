"""TODO(magedak): DO NOT SUBMIT without one-line documentation for hard_coded_request.

TODO(magedak): DO NOT SUBMIT without a detailed description of hard_coded_request.
"""

TEST_REQUEST = 'TEST'

BIGGEST_CUSTOMERS = '''{
"result": {
    "source": "agent",
    "resolvedQuery": "What is my biggest customer",
    "action": "yahooWeatherForecast",
    "actionIncomplete": false,
    "parameters": {
      "date-period": "",
      "number": "",
      "queried_table": "customer",
      "size": "top",
      "sort_by": ""
    }
  }
}
'''

TOP_WITHIN_TWO_WEEKS = '''{
  "result": {
    "source": "agent",
    "resolvedQuery": "Top 10 customers in the last two weeks",
    "action": "yahooWeatherForecast",
    "actionIncomplete": false,
    "parameters": {
      "date-period": "2017-05-06/2017-05-20",
      "number": "10",
      "queried_table": "customer",
      "size": "top",
      "sort_by": ""
    }
  }
}'''

LAST_Q_REVENUE = '''{
  "result": {
    "source": "agent",
    "resolvedQuery": "What's my revenue for the last quarter?",
    "action": "yahooWeatherForecast",
    "actionIncomplete": false,
    "parameters": {
      "date-period": "2017-01-01/2017-03-31",
      "number": "",
      "queried_table": "revenue",
      "size": "",
      "sort_by": ""
    }
  }
}'''

THREE_BIGGEST = '''{
"result": {
    "source": "agent",
    "resolvedQuery": "Give me my biggest 3 clients by number of orders",
    "action": "yahooWeatherForecast",
    "actionIncomplete": false,
    "parameters": {
      "date-period": "",
      "number": "3",
      "queried_table": "customer",
      "size": "top",
      "sort_by": "number of orders"
    }
  }
}'''

