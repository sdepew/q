from bot.commands.weather import *
from bot.commands.chuck import *

def test_weather():
    assert isinstance(weather(call_type="weather", zip_code="20170"), str)


def test_forecast():
    assert isinstance(weather(call_type="forecast", zip_code="20170"), str)


def test_chuck():
    assert isinstance(chuck(), str)
