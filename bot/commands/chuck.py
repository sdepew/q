import os
import requests
from bot.command_map import command_map

api_url = 'http://api.icndb.com/jokes/random'
params = {"escape":"javascript"}


@command_map.register_command()
def chuck(query=[]):
    '''
    Facts about Chuck Norris.
    *Usage:*
    `!chuck`
    '''
    request = requests.get(api_url, params).json()
    print(request['value']['joke'])
    response = request['value']['joke']
    return response
