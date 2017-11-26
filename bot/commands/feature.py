from bot.command_map import command_map

import requests
import random
import os
import json
import logging


logger = logging.getLogger()


github_qisims = ["You really think people will use that?", "Sweet!", "Nice!",
                 "That's gonna be my best feature yet!", "That's going to be the next `!chuck`!"]

github_user = os.environ['GITHUB_USER']
github_api_key = os.environ['GITHUB_API_KEY']


def get_data(url="", params={}, headers={}, data={}, auth=()):
    request = requests.get(url, params=params, headers=headers, auth=auth)
    headers['Accept'] = 'application/vnd.github.v3+json'
    if request.ok:
        return request
    else:
        return False


def post_data(url="", params={}, headers={}, data={}, auth=()):
    request = requests.post(url, json.dumps(params), headers=headers, auth=auth)
    headers['Accept'] = 'application/vnd.github.v3+json'
    headers['User-Agent'] = 'LEXmono-q'
    return request


@command_map.register_command()
def feature(query=[], user=""):
    '''
    Create a feature request on GitHub
    --------------------------------------------------------
    *Usage:*
    `!feature Do Something Awesome` Creates an issue with subject
    `Feature Request: Do Something Awesome`. You will be give a link
    to the issue where you can go add details.
    --------------------------------------------------------
    '''
    response = ""
    card_body = " ".join(query)
    create_card_url = "https://api.github.com/repos/{}/{}/issues".format(os.environ['GITHUB_OWNER'], os.environ['GITHUB_REPO']) #
    params = {'title': "Feature Request: {}".format(card_body),
              'labels': ["Feature Request"]}
    auth = (github_user, github_api_key)
    request = post_data(url=create_card_url, params=params, auth=auth)
    if request.ok:
        logger.debug("Git hub responded {}: {}".format(request.status_code, request.text))
        response += random.choice(github_qisims) + "\n"
        response += "Here is your Card: {}\nGo add some details.".format(request.json()['html_url'])
    else:
        logger.error("GitHub returned {}: {}".format(request.status_code, request.text))
        response += "GitHub didn't like that idea, it said {}: {}".format(request.status_code, request.text)
    return response
