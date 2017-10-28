import logging
import traceback

from bot.config import config

logger = logging.getLogger(__name__)


class CommandMap:
    def __init__(self):
        self.command_map = {}
        self.command_count = 0
        self.help_map = {}
        self.available_in_quiet = []
        self.listener_commands = []

    def _add_command(self, command, name,
                     help_text, available_in_quiet, hidden):

        # Command
        if not name:
            name = command.__name__
        self.command_map[name] = command

        # Help
        if not hidden:
            if not help_text:
                help_text = command.__doc__
            self.help_map[name] = help_text

        # Quiet
        if available_in_quiet:
            self.available_in_quiet.append(name)

    def register_command(self, name=None, help_text=None,
                         aliases=[], available_in_quiet=False,
                         hidden=False):
        def command_wrapper(command):
            self._add_command(command, name,
                              help_text, available_in_quiet,
                              hidden)
            for alias in aliases:
                self._add_command(command, alias,
                                  help_text,
                                  available_in_quiet, True)
            return command
        return command_wrapper

    def register_listener(self):
        def listener_wrapper(command):
            self.listener_commands.append(command)
            return command
        return listener_wrapper

    def process_command(self, user, message_parts):
        # lose the !, don't need it anymore
        message_parts[0] = message_parts[0].lstrip('!')
        command, arguments = message_parts[0], message_parts[1:]
        logger.debug("calling command: [" + command + "]")
        self.command_count += 1
        try:
            reply = self.call(command, arguments, user=user)
        except Exception as ex:
            logger.debug("failed original command: " + str(ex))
            logger.debug(traceback.format_exc())
            if config.domain == 'test' and command in self.command_map:
                reply = traceback.format_exc()
            elif "wolfram" in self.command_map:
                reply = self.call("wolfram", message_parts)
            else:
                reply = "I don't have any idea how to do that!"

        return reply

    def call(self, name=None, *args, **kargs):
        command = self.command_map.get(name, None)
        if not command:
            raise Exception("{} does not exist".format(name))
        return command(*args, **kargs)

    def call_listeners(self, *args, **kargs):
        return [listener(*args, **kargs) for listener
                in self.listener_commands]

    def help(self, name=None):
        help_text = self.help_map.get(name, None)
        if not help_text:
            return "I don't think this exists..."
        return help_text


command_map = CommandMap()
from bot.commands import *
