import requests
import os
from datetime import datetime
from bot.commons import degree_sign
from bot.command_map import command_map
from bot.commands.remember import read_from_dynamodb
# import boto3
# import io
# import re

import logging
logger = logging.getLogger()

# This will be used for plotting once we get numpy to import into Lambda successfully.
# import matplotlib.pyplot as plt
#
#
# def plot_forecast(returned_json):
#     file_key = "forecast/" + datetime.now().strftime("%Y%m%d%H%M%S-") + \
#                str(random.choice(range(123456,999999))) + ".png"
#     data = returned_json
#     forecast_temps = {datetime.fromtimestamp(i['dt']).strftime('%D - %H:%M'): i['main']['temp'] for i in data['list']}
#     plt.plot(forecast_temps.keys(), forecast_temps.values())
#     plt.xticks(rotation='vertical')
#     plt.gca().yaxis.grid(True)
#     # plt.show()
#
#     # Write image to memory instead of disk.
#     img_data = io.BytesIO()
#     plt.savefig(img_data, format='png')
#     img_data.seek(0)
#
#     # Upload to S3
#     s3 = boto3.resource('s3')
#     bucket = s3.Bucket(weather_forecast_bucket)
#     bucket.put_object(Body=img_data, ContentType='image/png', Key=file_key)
#     return "https://s3.amazonaws.com/{}/{}".format(weather_forecast_bucket,file_key)

weather_api_key = os.environ['WEATHER_API_KEY']
google_geocoding_api_key = os.environ['GOOGLE_GEOCODING_API']


def getWeatherLocation(input=[]):
    input = [i for i in input if i.lower() != "forecast"]
    address = "+".join(input)
    params = {'address': address,
              'key': google_geocoding_api_key
              }
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    request = requests.get(url, params=params)
    if request.ok:
        data = request.json()
        return data['results'][0]['geometry']['location']
    else:
        logger.error("HTTP Error from Google.\nError Code: {}\n Error: {}".format(request.status_code, request.content))
        return False


def get_weather(data, forecast=False):
    if forecast == False:
        params = {'lat': data['lat'],
                  'lon': data['lng'],
                  'APPID': weather_api_key,
                  'units': 'imperial'}
        return requests.get('https://api.openweathermap.org/data/2.5/weather', params=params).json()
    else:
        params = {'lat': data['lat'],
                  'lon': data['lng'],
                  'cnt': '16',
                  'APPID': weather_api_key,
                  'units': 'imperial'}
        # return requests.get('https://api.openweathermap.org/data/2.5/forecast/daily', params=params).json()
        return requests.get('https://api.openweathermap.org/data/2.5/forecast', params=params).json()


@command_map.register_command()
def weather(query=[], user=""):
    '''
    Get the weather.
    --------------------------------------------------------
    *Usage:*
    `!weather` - Returns Weather for Herndon and Auburn
    `!weather 20170 [forecast]` - Returns Weather for the zipcode.
    `!weather Herndon, VA [forecast]` - Returrns Weather for the City.
    You can also include the word "forecast" to get a detailed forecast.
    You can also set a preference so you dont have to type your location
    every time. Try `!help remember` for more details.
    --------------------------------------------------------
    '''
    command = ""
    preferred_location = ""
    try:
        preferred_location = read_from_dynamodb(['weather:'], user)['weather']
    except KeyError as weather_key_error:
        logger.debug("No Preference set: {}".format(weather_key_error))
        command += "No preference set, use `!remember weather:12345` to set your preference\n"
        pass
    if "forecast" in (x.lower() for x in query):
        if preferred_location:
            cleaned_location = getWeatherLocation([preferred_location])
            location = preferred_location
        else:
            cleaned_location = getWeatherLocation(query)
            location += " ".join([x for x in query if x.lower() != "forecast"])
        weather = get_weather(cleaned_location, forecast=True)
        command += "Here is your forecast for {}\n".format(location)
        if logger.getEffectiveLevel() == 10:  # If Debug
            command += "Latitude: {} Longitude: {}\n".format(cleaned_location['lat'], cleaned_location['lng'])
        command += "".join(["*<!date^{}^{}|{}>:* {}{}F - {}\n".format(x['dt'],
                            '{date_long_pretty} {time}',
            datetime.fromtimestamp(x['dt']).strftime('%m/%d %H:%M UTC'),
            x['main']['temp'],
            degree_sign,
            x['weather'][0]['description'].title()) for x in weather['list']])
    elif query:
        cleaned_location = getWeatherLocation(query)
        weather = get_weather(cleaned_location, forecast=False)
        if logger.getEffectiveLevel() == 10:  # If Debug
            command += "Latitude: {} Longitude: {}\n".format(cleaned_location['lat'], cleaned_location['lng'])
        command += "*It is currently* `{}{}F` in {}. *Today's Weather:* `{}` *High:* `{}{}F` *Low:* `{}{}F`".format(
            weather['main']['temp'],
            degree_sign,
            " ".join(query),
            weather['weather'][0]['description'].title(),
            weather['main']['temp_max'],
            degree_sign,weather['main']['temp_min'],
            degree_sign)
    else:
        if preferred_location:
            cleaned_location = getWeatherLocation([preferred_location])
            weather = get_weather(cleaned_location)
            if logger.getEffectiveLevel() == 10:  # If Debug
                command += "Here is your weather for {}\n".format(preferred_location)
                command += "Latitude: {} Longitude: {}\n".format(cleaned_location['lat'], cleaned_location['lng'])
            command += "*It is currently* `{}{}F` in {}. *Current Weather:* `{}` *High:* `{}{}F` *Low:* `{}{}F`\n".format(
                weather['main']['temp'],
                degree_sign,
                preferred_location,
                weather['weather'][0]['description'].title(),
                weather['main']['temp_max'],
                degree_sign,
                weather['main']['temp_min'],
                degree_sign)
        else:
            for item in [["Herndon", "VA"], ["Auburn", "AL"]]:
                cleaned_location = getWeatherLocation(item)
                weather = get_weather(cleaned_location)
                location = " ".join([x for x in item if x.lower() != "forecast"])
                if logger.getEffectiveLevel() == 10:  # If Debug
                    command += "Here is your weather for {}\n".format(location)
                    command += "Latitude: {} Longitude: {}\n".format(cleaned_location['lat'], cleaned_location['lng'])
                command += "*It is currently* `{}{}F` in {}. *Current Weather:* `{}` *High:* `{}{}F` *Low:* `{}{}F`\n".format(
                    weather['main']['temp'],
                    degree_sign,
                    " ".join(item),
                    weather['weather'][0]['description'].title(),
                    weather['main']['temp_max'],
                    degree_sign,
                    weather['main']['temp_min'],
                    degree_sign)
    return command
