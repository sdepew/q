from bot.command_map import command_map
import boto3
import botocore.exceptions
from datetime import datetime
import json
import logging
import requests


logger = logging.getLogger()

quote_bucket = 'qbot-287010246646'
file_key = 'quotes/' + datetime.now().strftime('%Y%m%d') + '-categories.json'


def s3_connect():
    s3 = boto3.resource('s3')
    return s3.Object(quote_bucket, file_key)


def get_data(url="", params={}, headers={}):
    request = requests.get(url, params=params, headers=headers)
    if request.ok:
        return request
    elif request.json():
        if request.json()['error']['code'] == 429:
            logger.warning("Quotes throttled us. We have to wait {}".format(request.json()))
    else:
        logger.error("Unable to get data from {} with params: {} and headers: {}. Error: {}".format(url,
                                                                                                    params,
                                                                                                    headers,
                                                                                                    request.content))
        return None


def get_categories():
    ''' Get Categories from Quotes.rest

    :returns data:
    '''
    url = 'http://quotes.rest/qod/categories'
    params = {}
    headers = {'Accept': 'application/json'}
    response = get_data(url=url, headers=headers)
    if response and response.ok:
        data = {x: y for x, y in response.json()['contents']['categories'].items()}
        try:
            assert isinstance(data, dict)
        except AssertionError as assertion_error:
            logger.error("Unable to get categories from quotes.rest: {}"
                         "Data received: {}".format(assertion_error, response['contents']['categories'].keys()))
            return None
    else:
        data = {'contents': {""}}
    return data


def store_quote_categories(input_json):
    '''
    Store categories in s3 as .json file.
    Returns the url or None

    :param input_json:
    :type input_json: dict
    :returns object_url:
    :type object_url: str
    :type object_url: None
    '''
    try:
        assert isinstance(input_json, dict)
    except AssertionError as assertion_error:
        logger.error("Input to store_quote_categories is not a dictionary: {}".format(assertion_error))
        return None
    binary_dict = json.dumps(input_json)
    object = s3_connect()
    object.put(Body=binary_dict)
    object_url = "https://s3.amazonaws.com/{}/{}".format(quote_bucket, file_key)
    return object_url


def retrieve_categories():
    '''Get today's categories from s3'''
    object = s3_connect()
    data = json.loads(object.get()['Body'].read().decode('utf-8'))
    return data


def check_categories():
    '''
    Check if the categories already exist for today.::

    :rtype: bool
    :returns: True or False
    '''
    s3 = boto3.resource('s3')
    try:
        s3.Object(quote_bucket, file_key).load()
    except botocore.exceptions.ClientError as file_error:
        if file_error.response['Error']['Code'] == "404":
            # The object does not exist, so return False.
            return False
        else:
            logger.error("Daily Category exists but we got a 404. - {}".format(file_error))
    else:
        print("Categories Exist")
        return True


def get_quote(category=""):
    url = 'http://quotes.rest/qod'
    params = {'category': category}
    return get_data(url, params=params)


def qotd(query=[], user=""):
    response = ""
    if query:
        if check_categories():
            categories = retrieve_categories()
        else:
            categories = get_categories()
            store_quote_categories(categories)
        for item in query:
            if item.lower() in categories.keys():
                request = get_quote(category=item)
                response += "{} - {}\n".format(request.json()['contents']['quotes'][0]['quote'],
                                             request.json()['contents']['quotes'][0]['author'])
        if response == "":
            response += "Sorry these are all we got: {}".format(["`{}`".format(x) for x in categories])
    else:
        request = get_quote()
        response += "{} - {}".format(request.json()['contents']['quotes'][0]['quote'],
                                     request.json()['contents']['quotes'][0]['author'])
    return response
