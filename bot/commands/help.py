from bot.command_map import command_map


@command_map.register_command()
def help(query=[], user=None):
    '''Prints this help section. You can also specify a command to get more information. i.e. `!help motivation`'''
    if not query:
        return 'I know how to do these: {}\n*Type `!help command` (Notice no ! on the command) for more details.*'.format(', '.join(
            sorted(["`!{}`".format(k) for k in command_map.help_map.keys()])))
    else:
        return '{}: {}'.format(query[0], command_map.help(query[0]))
