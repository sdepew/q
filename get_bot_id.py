#!/usr/bin/env python3
import os
import sys
try:
    import slackclient
except ImportError as ie:
    print("Please install slackclient first by running:")
    print("pip install -r requirements.txt")
    sys.exit(1)


if not os.environ.get('BOT_NAME'):
    print('Please set your BOT_NAME as a bash environment variable:')
    print('export BOT_NAME=\'HappyBot\'')
    sys.exit(1)

if not os.environ.get('SLACK_BOT_TOKEN'):
    print('Please set your SLACK_BOT_TOKEN as a bash environment variable:')
    print('export SLACK_BOT_TOKEN=\'ABS-YourTokenHere\'')
    sys.exit(1)

'''
Enter your case sensitive bot name here. https://api.slack.com/bot-users
'''
BOTS_NAME = os.environ.get('BOT_NAME')

slack_client = slackclient.SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


if __name__ == "__main__":
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOTS_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
    else:
        print("could not find bot user with the name " + BOTS_NAME)
