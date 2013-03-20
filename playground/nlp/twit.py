import sqlite3 as lite
import tweetstream
import csv
import sys
#from datetime import date
import time

# Ref: http://fr.slideshare.net/ericbrown/eric-d-brown-infs-890-spring-2012
#TODO General implementation: twitter collector according words stored in database (key | word | freq | sentiment stats | relevant score)
#TODO Changing from sqlite3 to sqlalchemy mysql
#TODO Sentiment analysis: Bayesian naive classifier with nltk

#TODO read it in configuration file
twitterUsername = 'XavierBruhiere'
twitterPassword = raw_input('Twitter password: ')

twitterWordFilter = []
wordListCsv = csv.reader(open('wordstofilter.csv', 'rb'))
for row in wordListCsv:
    #Add the 0th column of the current row to the list
    twitterWordFilter.append(row[0])

print "Filtering the following words: ", ', '.join(twitterWordFilter)

try:
    #Load the data base file (or make it if not found)
    #If dont set isolation level then we need to call
    #Db commit after every execute to save the transaction
    con = lite.connect('twitter.db', isolation_level=None)
    cur = con.cursor()
    #Get the sourceid (will be useful when we use multiple data sources)
    cur.execute("SELECT sourceid FROM sources where sourcedesc='twitter'")
    sourceid = cur.fetchone()
    sourceid = sourceid[0]

    with tweetstream.FilterStream(twitterUsername, twitterPassword, track=twitterWordFilter) as stream:
        for tweet in stream:
            tweettimestamp = time.mktime(time.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")) - time.timezone

            print stream.count, "(", stream.rate, "tweets/sec). ", tweet['user']['screen_name'], ':', tweet['text'].encode('ascii', 'ignore')
            #print tweet #Use for raw output
            try:
                cur.execute("INSERT INTO tweets(sourceid,username,tweet,timestamp) VALUES(?,?,?,?)", [sourceid, tweet['user']['screen_name'], tweet['text'].encode('ascii', 'ignore'), tweettimestamp])
            except:
                print "SQL Insert Error: Probably some encoding issue due to foreign languages"

except tweetstream.ConnectionError, e:
    print "Disconnected from twitter. Reason:", e.reason
except lite.Error, e:
    print "SQLite Error:", e
except:
    print "ERROR:", sys.exc_info()
finally:
    if con:
        con.close()
