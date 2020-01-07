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

import sys, json, time, coloredlogs, logging, twitter, requests, traceback, credentials, mysql.connector, requests_oauthlib

from tweet import Tweet
from docopt import docopt
from datetime import date
from mysql.connector import pooling

class Crawler(object):

    #class attributes
    date, pool, search_term, credentials = None, None, None, None

    logger = logging.getLogger(__name__)

    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "info": {"color": "white"}, "warning": {"color": "yellow"}, "success": {"color": "green"}, "error": {"color": "red"}
    }

    coloredlogs.DEFAULT_FIELD_STYLES = {
        "asctime": {"color": "green"}, "hostname": {"color": "magenta"}, "levelname": {"color": "blue", "bold": True}, "name": {"color": "blue"}
    }

    coloredlogs.install(
        datefmt = "%Y-%m-%d %H:%M:%S",
        fmt = "%(asctime)s %(levelname)s: %(message)s"
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
                resource_owner_secret = credentials.access_token_secretx
            )
            self.logger.info(f"Connected to Twitter API")
        except:
            self.logger.error(f"Twitter API authentication failed")
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
            self.logger.info(f"Connected to MySQL Server {db.get_server_info()} at {db.server_host}:{db.server_port}")
        except mysql.connector.Error as error:
            self.logger.error(error)

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
                if tweet.retweeted_status or tweet.text == "":
                    pass
                else:
                    client.logger.info(f"{tweet.text}")
                    mydb = client.pool.get_connection()
                    tweet.save_tweet(mydb)
                    tweet.save_to_graph(tweet, mydb, client.search_term)
                    mydb.close()
            except Exception as error:
                if status["limit"]:
                    client.logger.warning(f"{status['limit']['track']}")
                else:
                    print(json.dumps(status, indent = 4, sort_keys = True))
                    traceback.print_exc(file = sys.stdout)
                #break
        #time.sleep(0.1)

    client.pool.close()
    client.logger.info(f"MySQL connection is closed")
