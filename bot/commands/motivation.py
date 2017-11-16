import requests
from bot.command_map import command_map
import logging

logger = logging.getLogger()

ERROR_IMAGE = "https://imgs.xkcd.com/comics/christmas_back_home.png"


@command_map.register_command()
def motivation(query=[], user=None):
    '''
    Get a motivational image to get you're day going in the right direction.
    --------------------------------------------------------
    *Usage:*
    `!motivation`
    --------------------------------------------------------
    '''

    try:
        params = {'generate': 'true'}
        response = requests.get('http://inspirobot.me/api',
                                        params).text
        return response.replace('http://', 'https://')
    except requests.exceptions.RequestException as inpriroerror:
        logger.error('Failure getting image from inspirobot! {}'.format(inpriroerror))
        return ERROR_IMAGE
