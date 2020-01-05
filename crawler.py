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

import sys, json, time, logging, twitter, requests, traceback, credentials, mysql.connector, requests_oauthlib

from tweet import Tweet
from docopt import docopt
from datetime import date
from mysql.connector import pooling

class Crawler(object):

    #class attributes
    date, pool, search_term, credentials = None, None, None, None

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
        try:
            oauth = requests_oauthlib.OAuth1(
                        client_key = credentials.api_key,
                        client_secret = credentials.api_secret_key,
                        resource_owner_key = credentials.access_token_key,
                        resource_owner_secret = credentials.access_token_secret
                        )
            logging.info(f"Connected to Twitter API")
        except: 
            logging.info(f"Error: Twitter API authentication failed") 
        return oauth

    def connect_db(self):
        #connect to db
        try:
            self.pool = pooling.MySQLConnectionPool(
                            pool_name = "pool",
                            pool_size = 30,
                            autocommit = True,
                            buffered = True,
                            host = credentials.host,
                            user = credentials.user,
                            passwd = credentials.passwd
                            )
            db = self.pool.get_connection()
            logging.info(f"Connected to MySQL Server {db.get_server_info()} at {db.server_host}:{db.server_port}")
        except mysql.connector.Error as error:
            logging.info(error)

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
    oauth = client.connect_twitter()
    db = client.connect_db()
    response = client.twitter_stream(oauth)

    for status in response.iter_lines(chunk_size = 10000):
        if status:
            try:
                status = json.loads(status)
                tweet = Tweet(status)
                if tweet.language == "en":
                    logging.info(f"{tweet.text}")
                    mydb = client.pool.get_connection()
                    tweet.save_tweet(mydb)
                    tweet.save_to_graph(tweet, mydb, client.search_term)
                    mydb.close()
            except Exception as error:
                print(json.dumps(status, indent = 4, sort_keys = True))
                traceback.print_exc(file = sys.stdout)
                #break
        #time.sleep(0.1)

    client.pool.close()
    logging.info(f"MySQL connection is closed")
