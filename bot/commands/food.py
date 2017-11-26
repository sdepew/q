# -*- coding: utf-8 -*-
from __future__ import print_function

import requests
import os
import random
from datetime import datetime, timedelta, time
from bot.command_map import command_map
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.parse import urlencode
import logging
logger = logging.getLogger()

# https://www.yelp.com/developers/v3/manage_app
CLIENT_ID = os.environ["YELP_CLIENT_ID"]
CLIENT_SECRET = os.environ["YELP_CLIENT_SECRET"]

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'


# Defaults
DEFAULT_LOCATION = 'Herndon, VA'
SEARCH_LIMIT = 30


def obtain_bearer_token(host, path):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.

    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request(host, path, bearer_token, url_params=None):
    """Given a bearer token, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(bearer_token, term, location):
    """Query the Search API by a search term and location.

    Args:
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)


def get_business(bearer_token, business_id):
    """Query the Business API by a business ID.

    Args:
        bearer_token (str): OAuth bearer token, obtained using client_id and client_secret.
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)


def query_api(term, location):
    """Queries the API by the input values from the user.

    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
    """
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

    response = search(bearer_token, term, location)
    logger.debug('Response from search(): {}'.format(response))

    businesses = response.get('businesses')
    logger.debug('Response from response.get(\'businesses\'): {}'.format(businesses))
    if not businesses:
        return 'No businesses for {0} in {1} found.'.format(term, location)
    answer = "What about these for {} in {}:\n".format(term, location)
    answer += "".join(random.sample(["<{}|{}>\n".format(x['url'], x['name']) for x in businesses], 5))
    return answer


@command_map.register_command(aliases=['lunch', 'dinner'])
def food(query=[], user=""):
    '''
    Get food recommendations for a place.
    --------------------------------------------------------
    *Usage:*
    `!food [ZipCode] [City] [State]` returns food recommendations for a location.
    If no Zip Code is specified, it defaults to a location
    from a few predefined, at random.
    --------------------------------------------------------
    '''
    current_time = datetime.now() - timedelta(hours=5)
    if time(10, 30) <= current_time.time() <= time(13, 30):
        term = 'lunch'
    elif time(13, 31) <= current_time.time() <= time(22, 00):
        term = 'dinner'
    elif time(0, 0) <= current_time.time() <= time(10, 29):
        term = 'breakfast'
    else:
        term = 'bars'
    if query:
        location = ' '.join(query)
    else:
        location = random.choice(["Auburn, AL", "Herndon, VA", "Atlanta, GA"])
    try:
        result = query_api(term, location)
        logger.debug('Response from query_api({}, {}): {}'.format(term, location, result))
    except HTTPError as error:
        return "Uh oh! I found an error:\n    Code: {0}\n    {1}\n    {2}".format(error.code, error.url, error.read())
    return result
