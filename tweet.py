#!/usr/bin/env python

import re
import csv

from os import path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class Tweet(object):

    #class attributes
    tweet_id = None
    created_at = None
    text = None
    retweeted_status = None
    symbols = list()

    def __init__(self, status):
        self.tweet_id = status["id"]
        self.created_at = status["created_at"]
        self.text = status["text"].replace("\r", "").replace("\n", "")
        self.symbols = [item["text"].upper() for item in status["entities"]["symbols"]]
        if "retweeted_status" in status:
            self.retweeted_status = status["retweeted_status"]

    def save_tweet(self):
        #save processed tweet
        outfile = "tweets.csv"
        fieldnames = ["tweet_id", "created_at", "text", "symbols"]
        if path.exists(outfile):
            csvfile = open(outfile, "a+", encoding = "utf-8")
            writer = csv.DictWriter(f = csvfile, fieldnames = fieldnames)
        else:
            csvfile = open(outfile, "w+", encoding = "utf-8")
            writer = csv.DictWriter(f = csvfile, fieldnames = fieldnames)
            writer.writeheader()
        if self.retweeted_status:
            pass
        else:
            writer.writerow({
                "tweet_id": self.tweet_id, 
                "created_at": self.created_at, 
                "text": self.text,
                "symbols": ",".join(self.symbols)
            })
        csvfile.close()

    def save_to_graph(self, tweet, search_term):
        #save processed tweet
        outfile = "graph.csv"
        fieldnames = ["tweet_id", "created_at", "source", "target"]
        if path.exists(outfile):
            csvfile = open(outfile, "a+", newline = "\n", encoding = "utf-8")
            writer = csv.DictWriter(f = csvfile, fieldnames = fieldnames)
        else:
            csvfile = open(outfile, "w+", newline = "\n", encoding = "utf-8")
            writer = csv.DictWriter(f = csvfile, fieldnames = fieldnames)
            writer.writeheader()
        if tweet.retweeted_status:
            pass
        else:
            for symbol in tweet.symbols:
                source = re.sub("[^a-zA-Z]+", "", search_term).upper()
                target = symbol.upper()
                if source != target:
                    writer.writerow({
                        "tweet_id": tweet.tweet_id, 
                        "created_at": tweet.created_at, 
                        "source": source, 
                        "target": target
                    })
        csvfile.close()
