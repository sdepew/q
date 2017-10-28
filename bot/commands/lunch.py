import logging
from random import choice

from bot.command_map import command_map

from bot.config import config

logger = logging.getLogger(__name__)
team_choices = None
help_text = 'Figure out where to eat lunch, given a list of people.'

# Load lunch file
team_choices = config.load_json('configuration/lunch.json')
help_text += ' usage: lunch <{}>'.format('|'.join(team_choices.keys()))


@command_map.register_command(help_text=help_text,
                              available_in_quiet=True)
def lunch(query=[], user=None):
    favorites = []

    if team_choices:
        for person in query:
            if person in team_choices:
                # Cast individual choices as Set
                # to keep people from stacking votes
                favorites.extend(set(team_choices[person]))

        if not favorites:
            favorites = team_choices['default']

        return choice(favorites)

    return "I don't know; you pick!"
