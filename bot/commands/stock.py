from bot.command_map import command_map

import requests
import os
from datetime import datetime
import pytz

import logging
logger = logging.getLogger()

# Set current date in Eastern time as this is the Key for the Json returned.
today_date = datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d')


@command_map.register_command()
def stock(query=[], user=""):
    '''
    Get Stock Prices
    --------------------------------------------------------
    *Usage:*
    `!stock AMZN MSFT GOOG`
    --------------------------------------------------------
    '''
    response = ""
    if query:
        for symbol in query:
            params = {
                'function': 'TIME_SERIES_DAILY_ADJUSTED',
                'symbol': symbol,
                'apikey': os.environ['ALPHA_VANTAGE_API_KEY']
            }
            url = 'https://www.alphavantage.co/query'
            request = requests.get(url, params=params)
            if request.ok:
                data = next(iter(request.json()['Time Series (Daily)'].values()))
                try:
                    response += "============={}=============\n".format(symbol.upper())
                    response += "*Price:* `{}`*Opening:* `{}`" \
                                "*High:* `{}`*Low:* `{}`\n".format('${:,.2f}'.format(float(data['5. adjusted close'])),
                                                                     '${:,.2f}'.format(float(data['1. open'])),
                                                                     '${:,.2f}'.format(float(data['2. high'])),
                                                                     '${:,.2f}'.format(float(data['3. low'])))
                except KeyError as badkeys:
                    logger.error("EXCEPTION: KeyError {}\ndata: {}".format(badkeys, data))
                    return "KeyError from Alpha Vantage. Did they change something? {}".format(badkeys)
            else:
                logger.error("Unable to get Stock from Alpha Vantage."
                             "Error Code: {}\n Error: {}".format(request.status_code, request.content))
                response += "Unable to get stock price from Alpha Vantage for `{}`. Try again in a bit.".format(symbol)
        logger.debug("Returning Stock Info: {}".format(response))
    else:
        response += "Please enter one or more stock symbol(s). Type `!help stock` for more. `"
    return response


