from bot.command_map import command_map
from os import environ
import requests

import logging
logger = logging.getLogger()

api_key = environ['GOOGLE_NEWS_API']
Sources = {
    "general": ["reddit-r-all", "google-news"],
    "tech": ["techcrunch", "wired", "the-verge"],
    "sports": ["espn"],
    "politics": ["politico", "the-hill"],
    "music": ["mtv-news"],
    "science": ["national-geographic", "new-scientist", "next-big-future"],
    "health": ["medical-news-today"],
    "gaming": ["ign"],
    "business": ["fortune", "business-insider"]
}


def find_source(item):
    ''' Accepts a str Returns list of sources to search for'''
    response = []
    if item in Sources.keys():
        response.extend(Sources[item])
    return response


@command_map.register_command()
def news(query=[], user=""):
    '''
    Get the news.
    --------------------------------------------------------
    *Usage:*
    `!news` returns available sources.
    `!news tech business` will return tech and business news.
    `!news YourTerm` will query for that item and return results.
    --------------------------------------------------------
    '''
    response = ""
    if not query:
        return "I know these sources: {}".format(", ".join([x for x in Sources.keys()]))
    for term in query:
        if term in Sources.keys():
            response += "*{}:*\n".format(term.title())
            source_list = find_source(term)
            for source in source_list:
                try:
                    url = 'https://newsapi.org/v2/top-headlines'
                    params = {
                        'sources': source,
                        'language': 'en',
                        'apiKey': api_key
                    }
                    request = requests.get(url, params=params)
                    if request.ok:
                        data = request.json()
                        for index, article in enumerate(data['articles']):
                            if index < 3:
                                response += "<{}|{}>\n".format(article['url'], article['title'])
                    else:
                        response += "Unable to get news for {}. {}\n".format(source, request.status_code)
                except requests.exceptions.RequestException as request_exception:
                    logger.error("Unable to get request for {}. ERROR: {}".format(source, request_exception))
                    response += "Unable to get request for {}".format(source)
        else:
            try:
                url = 'https://newsapi.org/v2/everything'
                params = {
                    'q': term,
                    'language': 'en',
                    'apiKey': api_key,
                }
                request = requests.get(url, params=params)
                if request.ok:
                    data = request.json()
                    for index, article in enumerate(data['articles']):
                        if index < 5:
                            response += "<{}|{}>\n".format(article['url'], article['title'])
            except requests.exceptions.RequestException as request_exception:
                logger.error("Unable to get request for {}. ERROR: {}".format(term, request_exception))
                response += "Unable to get request for {}".format(term)
    if response == "":
        response += "https://s3.amazonaws.com/qbot-287010246646/images/fakenewsbitmoji.jpg"
    return response
