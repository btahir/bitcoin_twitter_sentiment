import re
import tweepy
import csv
import datetime
from tweepy import OAuthHandler
from textblob import TextBlob

class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = '6qOTLNu7v09CHNbCfH61Vg9HF'
        consumer_secret = 'W5PH4IQ6WV6y2eqzzvWR17gc3qWmFr6Y1HiEFbDUpJMNM0Tsix'
        access_token = '966467376546856960-eyGniFBu3oGPi5JmJd05stVnOkKbj1z'
        access_token_secret = 'YxQHrIjcBGq3SAzxewnS2Qr6PI0Qbw441QC5t5K0oKZcA'
 
        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
 
    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
 
    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
 
    def get_tweets(self, query, count = 10):
        '''
        Main function to fetch tweets and parse them.
        '''
        # empty list to store parsed tweets
        tweets = []
 
        try:
            # call twitter api to fetch tweets
            fetched_tweets = self.api.search(q = query, count = count)
 
            # parsing tweets one by one
            for tweet in fetched_tweets:
                # empty dictionary to store required params of a tweet
                parsed_tweet = {}
 
                # saving text of tweet
                parsed_tweet['text'] = tweet.text
                # saving sentiment of tweet
                parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
 
                # appending parsed tweet to tweets list
                if tweet.retweet_count > 0:
                    # if tweet has retweets, ensure that it is appended only once
                    if parsed_tweet not in tweets:
                        tweets.append(parsed_tweet)
                else:
                    tweets.append(parsed_tweet)
 
            # return parsed tweets
            return tweets
 
        except tweepy.TweepError as e:
            # print error (if any)
            print("Error : " + str(e))
 
def sent_check():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query = 'Bitcoin', count = 1000)
 
    # picking positive tweets from tweets
    ptweets = [tweet for tweet in tweets if tweet['sentiment'] == 'positive']
    
    # picking negative tweets from tweets
    ntweets = [tweet for tweet in tweets if tweet['sentiment'] == 'negative']
    
    # store variables
    pos = 100*len(ptweets)/len(tweets)
    neg = 100*len(ntweets)/len(tweets)
    neut = 100*(len(tweets) - len(ntweets) - len(ptweets))/len(tweets)
    
    return [pos, neg, neut]

def insert_csv(a):
    a.insert(0, datetime.datetime.today().strftime('%Y-%m-%d'))

    with open(r'bitcoin_sentiment_history.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow(a)

 
if __name__ == "__main__":
    # calling sent_check function
    main_array = [0]*4
    
    for i in range(10):
        # get sent_nums
        new_array = sent_check()
        main_array[0] += new_array[0]
        main_array[1] += new_array[1]
        main_array[2] += new_array[2]

    # final values
    main_array[0] = main_array[0]/10
    main_array[1] = main_array[1]/10
    main_array[2] = main_array[2]/10
    main_array[3] = sum(main_array)
        
    # percentage of positive tweets
    print("Avg Positive tweets percentage: {} %".format(main_array[0]))
    # percentage of negative tweets
    print("Avg Negative tweets percentage: {} %".format(main_array[1]))
    # percentage of neutral tweets
    print("Avg Neutral tweets percentage: {} %".format(main_array[2]))
    print("Avg Total Check: {} %".format(main_array[3]))

    insert_csv(main_array)
        