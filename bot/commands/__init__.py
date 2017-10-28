import pkgutil
import inspect

__all__ = []

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    command_module = loader.find_module(name).load_module(name)

    for command_name, value in inspect.getmembers(command_module):
        if command_name.startswith('__'):
            continue

        globals()[command_name] = value
        __all__.append(command_name)
