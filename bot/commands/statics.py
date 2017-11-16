from bot.command_map import command_map

@command_map.register_command()
def shrug(query=[]):
    """
    `¯\_(ツ)_/¯`
    """
    return "¯\_(ツ)_/¯ " + " ".join(query)
