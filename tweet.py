#!/usr/bin/env python

import re, calendar, logging, mysql.connector as mysql

from os import path
from textblob import TextBlob
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class Tweet(object):

    #class attributes
    date, time, text, weekday, user_id, user_name, tweet_id, user_location, retweeted_status = None, None, None, None, None, None, None, None, None
    symbols = list()

    logging.basicConfig(
        level = logging.INFO,
        datefmt = "%Y-%m-%d %H:%M:%S",
        format = "%(asctime)s %(levelname)s: %(message)s"
        )

    def __init__(self, status):
        created_at = datetime.strptime(status["created_at"], "%a %b %d %H:%M:%S %z %Y")
        self.date = created_at.date()
        self.time = created_at.time()
        self.tweet_id = status["id"]
        self.user_id = status["user"]["id"]
        self.user_name = status["user"]["name"]
        self.text = self.clean_tweet(status["text"])
        self.user_location = status["user"]["location"]
        self.weekday = calendar.day_name[created_at.weekday()]
        self.symbols = [item["text"].upper() for item in status["entities"]["symbols"]]
        self.retweeted_status = status["retweeted_status"] if "retweeted_status" in status else None
        sentiment = self.get_tweet_sentiment(self.text)
        self.polarity = sentiment.polarity
        self.subjectivity = sentiment.subjectivity

    def clean_tweet(self, tweet): 
        #clean tweet text by removing links and special characters
        return " ".join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet).split())

    def get_tweet_sentiment(self, tweet): 
        #function to classify sentiment of passed tweet
        analysis = TextBlob(tweet)
        return analysis.sentiment

    def save_tweet(self, mydb):
        #save processed tweet
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS twitter")
        cursor.execute("USE twitter")
        cursor.execute("CREATE TABLE IF NOT EXISTS tweets (tweet_id VARCHAR(255) PRIMARY KEY, created_date DATE, created_time TIME, weekday VARCHAR(255), text VARCHAR(255), polarity FLOAT, subjectivity INT, symbols VARCHAR(255))")

        if self.retweeted_status:
            pass
        else:
            try:
                sql = "INSERT INTO tweets (tweet_id, created_date, created_time, weekday, text, polarity, subjectivity, symbols) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                values = (self.tweet_id, self.date, self.time, self.weekday, self.text, self.polarity, self.subjectivity, ",".join(self.symbols))
                cursor.execute(sql, values)
            except mysql.Error as error:
                if error.errno == mysql.errorcode.ER_DUP_ENTRY:
                    logging.info(error)
                else:
                    raise
        cursor.close()

    def save_to_graph(self, tweet, mydb, search_term):
        #save processed tweet
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS twitter")
        cursor.execute("USE twitter")
        cursor.execute("CREATE TABLE IF NOT EXISTS graph (id INT AUTO_INCREMENT PRIMARY KEY, tweet_id VARCHAR(255), created_date DATE, created_time TIME, weekday VARCHAR(255), source VARCHAR(255), target VARCHAR(255))")

        if tweet.retweeted_status:
            pass
        else:
            for source in tweet.symbols:
                for target in tweet.symbols:
                    source = source.upper()
                    target = target.upper()
                    if source != target:
                        sql = "INSERT INTO graph (tweet_id, created_date, created_time, weekday, source, target) VALUES (%s, %s, %s, %s, %s, %s)"
                        values = (self.tweet_id, self.date, self.time, self.weekday, source, target)
                        cursor.execute(sql, values)
        cursor.close()
