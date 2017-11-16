'''
A file for common variables. Please keep these alphabetical.
'''

from datetime import datetime, time
import requests

degree_sign= u'\N{DEGREE SIGN}'
qisims = ["Don't touch that! It's my lunch!", "Why are the doors opening?", "I wish I could make you vanish."]

DEFAULT_LOCATION = 'Herndon, VA'

current_time = datetime.now().time()
if current_time >= time(10,30) and current_time <= time(13,30):
    DEFAULT_TERM = 'lunch'
elif current_time >= time(13,31) and current_time <= time(2,00):
    DEFAULT_TERM = 'dinner'
else:
    DEFAULT_TERM = 'breakfast'

# weather.py configs
weather_forecast_bucket = "qbot-287010246646"

# Common Functions 
def tiny_url(url):
    endpoint = 'http://tinyurl.com/api-create.php'
    params = {'url': url}
    r = requests.get(endpoint, params=params)
    return r.text
