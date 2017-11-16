"""
Q, (standing for Quartermaster), is a job title rather than a name.
Q is the head of Q Branch, the research and development division
of the British Secret Service MI6.
"""

import os
import json
import urllib
import re
import requests
import random
from datetime import datetime, timedelta
import time
from bot.commons import *
from bot.command_map import command_map
from slackclient import SlackClient
from collections import deque

# Python Logging stuff
import logging
logger = logging.getLogger()
LogLevel = os.environ['LOG_LEVEL']
if LogLevel == "DEBUG":
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
def log_handler(event):
    logger.info('EVENT: {}'.format(event))
    return None

# Grab the various keys from the lambda env variables.
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_NAME = os.environ["BOT_NAME"]
BOT_ID = os.environ["BOT_ID"]

class Bot:
    def __init__(self):
        self.bot_name = os.environ['BOT_NAME']
        self.token = os.environ.get('BOT_TOKEN')
        self.BOT_ID = os.environ.get("BOT_ID")
        self.AT_BOT = "<@" + self.BOT_ID + ">"

        self.client = SlackClient(self.token)
        logger.debug("Slack CLient Created:\nName: {}\nToken: {}\nBot Id: {}\nAt Id: {}".format(self.bot_name,
            self.token, self.BOT_ID, self.AT_BOT))

    # def handle_command(self, command, channel):
    def handle_command(self, data, context):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        # This is needed for Slack to authorize us. Should only run once
        # But we may as well keep this, just in case.
        if "challenge" in data:
            return data["challenge"]

        # Grab the Slack event data.
        logger.debug("New Request Received: {}\n<===============================>".format(data))
        logger.debug("Available Commands:\n<===============================>{}".format(command_map.command_map))
        slack_event = data['event']
        command_raw_list = slack_event['text'].split(" ") # Input made into a list for parsing into its parts.
        command = command_raw_list[0] # Actual command. Starts with ! and ends at first space.
        query = command_raw_list[1::] # Everything after the first space.
        channel = slack_event['channel']
        current_time = datetime.fromtimestamp(float(slack_event['event_ts'])) - timedelta(hours=5)

        if command.startswith("!") and \
                command.lstrip('!') in command_map.command_map:
            logger.debug("Command found in Command Map: {}".format(command))
            response = self.call(command, query)
        elif command.startswith(self.AT_BOT) and \
                command.startswith(self.AT_BOT).lstrip(self.AT_BOT) \
                in command_map.command_map:
            logger.debug("Command directed at bot and found in Comand Map: {}".format(command))
            response = self.call(command)
        else:
            logger.debug("Command not directed at bot returning None")
            return None
        logger.debug("Posting to Slack API:\nChannel: {}\nResponse:{}\n".format(channel, response))
        self.client.api_call("chat.postMessage",
                             channel=channel,
                             text=response,
                             as_user=False)

    def call(self, name=None, *args, **kwargs):
        command = command_map.call(name.lstrip('!'), *args, **kwargs)
        if not command:
            raise Exception("{} does not exist".format(name))
        return command



def q_input(data, context):
    q = Bot()
    q.handle_command(data, context)
#    return "200 OK"
