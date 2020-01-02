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

import re
import csv
import json
import twitter
import pandas as pd
from os import path
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

    def save_tweet(self, tweet):
        #save processed tweet
        outfile = "tweets.out"
        fieldnames = ["tweet_id", "created_at", "text"]
        if path.exists(outfile):
            f = open(outfile, "a+", encoding = "utf-8")
            writer = csv.DictWriter(f, fieldnames = fieldnames)
        else:
            f = open(outfile, "w+", encoding = "utf-8")
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writeheader()

        if tweet.retweeted_status:
            pass
        else:
            writer.writerow({
                "tweet_id": tweet.tweet_id,
                "created_at": tweet.created_at,
                "text": tweet.text
            })
        f.close()

    def save_to_graph(self, tweet):
        #save processed tweet
        outfile = "graph.out"
        fieldnames = ["tweet_id", "created_at", "source", "target"]
        if path.exists(outfile):
            f = open(outfile, "a+", encoding = "utf-8")
            writer = csv.DictWriter(f, fieldnames = fieldnames)
        else:
            f = open(outfile, "w+", encoding = "utf-8")
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writeheader()

        if tweet.retweeted_status:
            pass
        else:
            for symbol in tweet.symbols:
                writer.writerow({
                    "tweet_id": tweet.tweet_id,
                    "created_at": tweet.created_at,
                    "source": re.sub("[^a-zA-Z]+", "", self.search_term).upper(),
                    "target": symbol.upper()
                })
        f.close()

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
        tweet = Tweet(status)
        client.save_tweet(tweet)
        client.save_to_graph(tweet)
