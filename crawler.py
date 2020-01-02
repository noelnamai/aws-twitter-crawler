#!/usr/bin/env python

"""
Usage:
    crawler.py --credentials-file <FILE> --search-term <STRING>
    crawler.py (-h | --help)
    crawler.py (-v | --version)

Options:
    -h --help                   Show this screen and exit.
    -v --version                Show version and exit.
    --search-term=STRING        The term to search Twitter API by.
    --credentials-file=FILE     Path to credentials file.
"""

import json
import logging
import twitter
import pandas as pd

from tweet import Tweet
from docopt import docopt
from datetime import date

class Crawler(object):
    #class attributes
    date = None
    search_term = None
    credentials = None

    def __init__(self, args):
        #read credentials file
        credentials = args["--credentials-file"]
        with open(credentials, "r") as obj:
            data = obj.read()
        self.date = str(date.today())
        self.credentials = json.loads(data)
        self.search_term = args["--search-term"]

        logging.basicConfig(
            level = logging.INFO,
            datefmt = "%m/%d/%Y %H:%M:%S", 
            format = "%(asctime)s %(levelname)s: %(message)s"
            )

    def log_into_twitter(self):
        #loginto the twitter API and return the api object
        credentials = self.credentials
        api = twitter.Api(
                consumer_key = credentials["api_key"],
                consumer_secret = credentials["api_secret_key"],
                access_token_key = credentials["access_token_key"],
                access_token_secret = credentials["access_token_secret"]
                )
        return api

if __name__ == "__main__":
    args = docopt(__doc__, version='Twitter Crawler Version:1.0')
    client = Crawler(args)
    api = client.log_into_twitter()
    #print(twitter.ratelimit.RateLimit())
    results = api.GetSearch(
                lang = "en",
                count = 100,
                return_json = True,
                result_type = "recent",
                since = client.date,
                term = client.search_term
                )
    #statuses = json.dumps(results["statuses"][0], indent = 4, sort_keys = True)
    for status in results["statuses"]:
        if len(status["entities"]["symbols"]) > 0:
            tweet = Tweet(status)
            logging.info(f"crawler processing {tweet.tweet_id} created at: {tweet.created_at}")
            tweet.save_tweet()
            tweet.save_to_graph(tweet = tweet, search_term = client.search_term)
