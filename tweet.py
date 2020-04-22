#!/usr/bin/env python3

import re
import util
import calendar
import mysql.connector as mysql

from os import path
from textblob import TextBlob
from datetime import datetime
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class Tweet(object):

    def __init__(self, status):
        created_at = datetime.strptime(status["created_at"], "%a %b %d %H:%M:%S %z %Y")
        text       = status["extended_tweet"]["full_text"] if status["truncated"] else status["text"]

        self.symbols          = list()
        self.date             = created_at.date()
        self.time             = created_at.time()
        self.weekday          = calendar.day_name[created_at.weekday()]
        self.text             = self.clean_tweet(text)
        self.tweet_id         = status["id"]
        self.language         = status["lang"]
        self.user_id          = status["user"]["id"]
        self.user_name        = status["user"]["name"]
        self.user_location    = status["user"]["location"]
        self.symbols          = [item["text"].upper() for item in status["entities"]["symbols"]]
        self.retweeted_status = status["retweeted_status"] if "retweeted_status" in status else None

        self.polarity, self.subjectivity = self.get_tweet_sentiment(self.text)

    def clean_tweet(self, tweet):
        """
        clean tweet text by removing links and special characters
        """
        cleaned_tweet = " ".join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", tweet).split())

        return cleaned_tweet

    def get_tweet_sentiment(self, tweet):
        """
        function to classify sentiment of passed tweet
        """
        blob         = TextBlob(tweet)
        polarity     = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        return polarity, subjectivity

    def save_tweet(self, mydb):
        """
        save processed tweet
        """
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS twitter")
        cursor.execute(
            """
            USE twitter
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tweets
            (
                tweet_id        VARCHAR(255), 
                created_date    DATE, 
                created_time    TIME, 
                weekday         VARCHAR(255), 
                full_text       TEXT, 
                polarity        FLOAT, 
                subjectivity    INT, 
                symbols         VARCHAR(255),
                PRIMARY KEY(tweet_id)
            );
            """
        )

        try:
            sql = "INSERT INTO tweets (tweet_id, created_date, created_time, weekday, full_text, polarity, subjectivity, symbols) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            values = (self.tweet_id, self.date, self.time, self.weekday, self.text, self.polarity, self.subjectivity, ",".join(self.symbols))
            cursor.execute(sql, values)
        except mysql.Error as error:
            if error.errno == mysql.errorcode.ER_DUP_ENTRY:
                util.logger.error(error)
            else:
                raise

        cursor.close()

    def save_to_graph(self, tweet, mydb, search_term):
        """
        save processed tweet
        """
        cursor = mydb.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS twitter")
        cursor.execute(
            """
            USE twitter
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS graph
            (
                id              INT AUTO_INCREMENT, 
                tweet_id        VARCHAR(255), 
                created_date    DATE, 
                created_time    TIME, 
                weekday         VARCHAR(255), 
                source          VARCHAR(255), 
                target          VARCHAR(255),
                PRIMARY KEY(id)
            );
            """
        )

        for source in tweet.symbols:
            for target in tweet.symbols:
                source = source.upper()
                target = target.upper()
                if source != target:
                    try:
                        sql = "INSERT INTO graph (tweet_id, created_date, created_time, weekday, source, target) VALUES (%s, %s, %s, %s, %s, %s)"
                        values = (self.tweet_id, self.date, self.time, self.weekday, source, target)
                        cursor.execute(sql, values)
                    except mysql.Error as error:
                        if error.errno == mysql.errorcode.ER_DUP_ENTRY:
                            util.logger.error(error)
                        else:
                            raise

        cursor.close()
