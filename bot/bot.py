import os
from time import sleep

from bot.command_map import command_map
from slackclient import SlackClient


class Bot:
    def __init__(self):
        self.token = os.environ.get('SLACK_BOT_TOKEN')
        self.BOT_ID = os.environ.get("BOT_ID")
        # instantiate Slack & Twilio clients
        self.client = SlackClient(self.token)
        self.AT_BOT = "<@" + self.BOT_ID + ">"

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        if command.startswith("!") and command.lstrip('!') in command_map.command_map:
            response = self.call(command)
        elif command.startswith(self.AT_BOT) and command.startswith(self.AT_BOT).lstrip(self.AT_BOT) in command_map.command_map:
            response = self.call(command)
        else:
            response = "Yeah, I'm definitely not working. Maybe @aaron can fix me."
        self.client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def call(self, name=None, *args, **kwargs):
        from IPython import embed
        command = command_map.call(name.lstrip('!'), *args, **kwargs)
        # embed()
        if not command:
            raise Exception("{} does not exist".format(name))
        return command

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message begins
            with a '!' and the command is in the command map.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and output['text'].lstrip('!') in command_map.command_map:
                    # return text after the @ mention, whitespace removed
                    return output['text'].strip().lower(), output['channel']
        return None, None

    def run(self, slack_client):
        read_websocket_delay = 1  # 1 second delay between reading from firehose
        if slack_client.rtm_connect():
            print("q, at your service!")
            while True:
                command, channel = self.parse_slack_output(slack_client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                sleep(read_websocket_delay)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

q = Bot()
