from bot.command_map import command_map


@command_map.register_command()
def help(query=[], user=None):
    '''Prints this help section'''
    if not query:
        return 'I know how to do these: {}'.format(', '.join(
            sorted(["!" + k for k in command_map.help_map.keys()])))
    else:
        return '{}: {}'.format(query[0], command_map.help(query[0]))
