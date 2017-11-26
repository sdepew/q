from collections import namedtuple

degree_sign = u'\N{DEGREE SIGN}'
shrug_variable = '¯\_(ツ)_/¯'
qisims = ["Don't touch that! It's my lunch!", "Why are the doors opening?", "I wish I could make you vanish."]

DEFAULT_LOCATION = 'Herndon, VA'

# weather.py configs
weather_forecast_bucket = "qbot-287010246646"


def prepare_response(text="", attachment=""):
    """
    Take inputs of function and return them as named tuple.
    This allows us to return both an attachment and/or text.

    Args:
        text: str - What should be output to a line by Q.
        attachment: str, json format. What will build the attachment.

    Returns:
        Named tuple with Args text and attachment.

    Raises:
        KeyError: Raises an exception.
    """
    tuple_response = namedtuple('tuple_response', 'text attachment')
    response = tuple_response(text=text, attachment=attachment)
    return response


def variable_exists(variable):
    if variable in locals() or variable in globals():
        return True
    else:
        return False
