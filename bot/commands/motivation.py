import logging

import requests

from bot.command_map import command_map

logger = logging.getLogger(__name__)
ERROR_IMAGE = 'https://i.imgur.com/fpxhBjh.jpg'

@command_map.register_command()
def motivation(query=[], user=None):
    '''Get a motivation image. Usage: !motivation'''

    try:
        params = {'generate': 'true'}
        inspiro_response = requests.get('http://inspirobot.me/api', params).text
        return inspiro_response.replace('http://', 'https://')
    except requests.exceptions.RequestException as e:
        logger.error('Failure getting image from inspirobot! {}'.format(e))
        return ERROR_IMAGE
