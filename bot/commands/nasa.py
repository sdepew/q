import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os
from datetime import datetime
import random
from bot.command_map import command_map


# Retry method for Python Requests.
def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504),
        session=None,
        params=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.params = params
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


@command_map.register_command()
def nasa(query=[], user=""):
    ''' Get NASA's Picture of the Day.
    --------------------------------------------------------
    *Usage:*
    `!nasa`
    --------------------------------------------------------
    '''
    nasa_url = 'https://api.nasa.gov/planetary/apod'
    params = {"api_key": os.environ["NASA_API_KEY"]}
    request = requests_retry_session(params=params).get(nasa_url)

    if request.status_code == 200:
        data = request.json()
        response = "Here is NASA's Picture of the day.\n{}".format(data['hdurl'])
    else:
        response = "Nasa said nope. HTTP Status code {}".format(request.status_code)
    return response


@command_map.register_command()
def mars(query=[], user=""):
    ''' Get a random picture of Mars.
    --------------------------------------------------------
    *Usage:*
    `!nasa`
    --------------------------------------------------------
    '''
    try:
        year = random.choice(range(2012, datetime.now().year))
        month = random.choice(range(1, 12))
        day = random.choice(range(1, 31))
        mars_date = datetime(year, month, day).strftime("%Y-%m-%d")
    except Exception as inerr:
        return "Nasa gave us an error, maybe they changed something?: {}".format(inerr)
    nasa_url = 'https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos'
    params = {"earth_date": mars_date, "api_key": os.environ["NASA_API_KEY"]}
    request = requests_retry_session(params=params).get(nasa_url)
    data = request.json()
    if len(data['photos']) > 0:
        random_image = random.choice(data['photos'])
        image_url = random_image['img_src']
        rover = random_image['rover']['name']
        response = "{} | {}.\n{}\n".format(rover, mars_date, image_url)
        return response
    else:
        mars()
