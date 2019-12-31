#!/usr/bin/env python

class Tweet(object):

    #class attributes
    tweet_id = None
    created_at = None
    text = None
    retweeted_status = None
    symbols = list()

    def __init__(self, status):
        self.text = status["text"]
        self.tweet_id = status["id"]
        self.created_at = status["created_at"]
        self.symbols = [item["text"] for item in status["entities"]["symbols"]]
        if "retweeted_status" in status:
            self.retweeted_status = status["retweeted_status"]
