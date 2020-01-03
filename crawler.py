#!/usr/bin/env python

"""
Usage:
    crawler.py --search-term <STRING>
    crawler.py (-h | --help)
    crawler.py (-v | --version)

Options:
    -h --help                   Show this screen and exit.
    -v --version                Show version and exit.
    --search-term=STRING        The term to search Twitter API by.
"""

import sys
import traceback
import json
import logging
import twitter
import requests
import credentials
import requests_oauthlib
import mysql.connector

from tweet import Tweet
from docopt import docopt
from datetime import date

class Crawler(object):
    #class attributes
    date = None
    search_term = None
    credentials = None

    logging.basicConfig(
        level = logging.INFO,
        datefmt = "%Y-%m-%d %H:%M:%S",
        format = "%(asctime)s %(levelname)s: %(message)s"
        )

    def __init__(self, args):
        self.date = str(date.today())
        self.search_term = args["--search-term"]

    def connect_twitter(self):
        #loginto the twitter API and return the api object
        oauth = requests_oauthlib.OAuth1(
                    client_key = credentials.api_key,
                    client_secret = credentials.api_secret_key,
                    resource_owner_key = credentials.access_token_key,
                    resource_owner_secret = credentials.access_token_secret
                    )
        logging.info(f"Crawler has established a connection to Twitter API")
        return oauth

    def connect_db(self):
        #connect to db
        try:
            mydb = mysql.connector.connect(
                        host = credentials.host,
                        user = credentials.user,
                        passwd = credentials.passwd,
                        autocommit = True,
                        pool_size = 10,
                        buffered = True
                        )
            logging.info(f"Crawler has established a connection to MySQL Database")
        except mysql.connector.Error as error:
            logging.info(error)
        return mydb

    def twitter_stream(self, oauth):
        #get twitter stream with search term(s)
        response = requests.post(
                        stream = True,
                        auth = oauth,
                        timeout = 60,
                        url = "https://stream.twitter.com/1.1/statuses/filter.json",
                        data = {"track": self.search_term}
                        )
        return response

if __name__ == "__main__":
    args = docopt(__doc__, version='Twitter Crawler Version:1.0')
    client = Crawler(args)
    mydb = client.connect_db()
    oauth = client.connect_twitter()
    response = client.twitter_stream(oauth)

    for status in response.iter_lines(chunk_size = 10000):
        if status:
            try:
                status = json.loads(status)
                tweet = Tweet(status)
                if len(tweet.symbols) > 0:
                    logging.info(f"Crawler processing {tweet.tweet_id} created on {tweet.date} at {tweet.time}")
                    tweet.save_tweet(mydb)
                    tweet.save_to_graph(tweet, mydb, client.search_term)
            except Exception as error:
                traceback.print_exc(file = sys.stdout)
                break

    mydb.close()
    logging.info(f"MySQL connection is closed")
