from bot.commands.weather import *
from bot.commands.chuck import *
from bot.commands.motivation import motivation


def test_weather():
    assert isinstance(weather(query=["Auburn", "AL"]), str)


def test_forecast():
    assert isinstance(weather(query=["Auburn", "AL", "forecast"]), str)


def test_chuck():
    assert isinstance(chuck(), str)


def test_motivation():
    assert isinstance(motivation(), str)

