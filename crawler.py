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
import json
import twitter
from docopt import docopt
from datetime import date

class Crawler(object):
    #class attributes
    date = ""
    search_term = ""
    credentials = None

    def __init__(self, args):
        #read credentials file
        credentials = args['--credentials-file']
        with open(credentials, "r") as obj:
            data = obj.read()
        self.date        = str(date.today())
        self.credentials = json.loads(data)
        self.search_term = args['--search-term']

    def log_into_twitter(self):
        #loginto the twitter API and return the api object
        credentials = self.credentials
        api = twitter.Api(
                consumer_key        = credentials["api_key"],
                consumer_secret     = credentials["api_secret_key"],
                access_token_key    = credentials["access_token_key"],
                access_token_secret = credentials["access_token_secret"]
                )
        return api

if __name__ == '__main__':
    args = docopt(__doc__, version='Twitter Crawler Version:1.0')
    client = Crawler(args)
    api = client.log_into_twitter()

    #print(twitter.ratelimit.RateLimit())

    results = api.GetSearch(
                lang        = "en",
                count       = 10,
                return_json = True,
                result_type = "recent",
                since       = client.date,
                term        = client.search_term
                )

    #statuses = json.dumps(results["statuses"], indent = 4, sort_keys = True)

    for status in results["statuses"]:
        symbols    = [item["text"] for item in status["entities"]["symbols"]]
        for symbol in symbols:
            source     = re.sub("[^a-zA-Z]+", "", client.search_term).upper()
            target     = symbol
            id         = status["id"]
            text       = status["text"]
            created_at = status["created_at"]

            print(f"id: {id} \t created_at: {created_at} \t source: {source} \t target: {target}")
