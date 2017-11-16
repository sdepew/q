import requests
from bot.command_map import command_map

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
        inspiro_response = requests.get('http://inspirobot.me/api',
                                        params).text
        return inspiro_response.replace('http://', 'https://')
    except requests.exceptions.RequestException as e:
        logger.error('Failure getting image from inspirobot! {}'.format(e))
        return ERROR_IMAGE
