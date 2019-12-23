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
import twitter
from docopt import docopt

class Crawler(object):
    #class attributes
    search_term = ""
    credentials = None

    def __init__(self, args):
        #read credentials file
        credentials = args['--credentials-file']
        with open(credentials, "r") as obj:
            data = obj.read()
        self.credentials = json.loads(data)
        self.search_term = args['--search-term']

    def log_into_twitter(self):
        #loginto the twitter API and return the api object
        api = twitter.Api(
                consumer_key=self.credentials["api_key"],
                consumer_secret=self.credentials["api_secret_key"],
                access_token_key=self.credentials["access_token_key"],
                access_token_secret=self.credentials["access_token_secret"],
                sleep_on_rate_limit=True
                )
        return api

if __name__ == '__main__':
    args = docopt(__doc__, version='Twitter Crawler Version:1.0')
    client = Crawler(args)
    api = client.log_into_twitter()

    #print(twitter.ratelimit.RateLimit())

    results = api.GetSearch(
                lang = "en",
                count = 10,
                return_json = True,
                since = "2014-07-19",
                result_type = "recent",
                term = client.search_term
                )

    #statuses = json.dumps(results["statuses"], indent = 4, sort_keys = True)

    for status in results["statuses"]:
        id = status["id"]
        created_at = status["created_at"]
        text = status["text"]

        print(f"id: {id} \t created_at: {created_at} \t text: {text}")
