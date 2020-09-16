import streamlit as st
import re
from PIL import Image
import tweepy as tw
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns

ACCESS_TOKEN = '#credentials'
ACCESS_TOKEN_SECRET = '#credentials'
CONSUMER_KEY = '#credentials'
CONSUMER_SECRET = '#credentials'

auth = tw.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tw.API(auth, wait_on_rate_limit=True)

st.title("TWITTER SENTIMENT ANALYSIS APP")
st.markdown("""
	 This Data-App fetches Tweets via *Twitter API* and predicts sentiment on a particular topic provided by *User.*
	***Please provide input in the left pane and wait untill Tweets are being fetched.***
	""")

st.sidebar.title("User-Input-Interface")
search_words = st.sidebar.text_input("Input Topic (Ex. #Covid-19 or #wildfire)","#SSR")

agree = st.sidebar.checkbox("Include Retweets in Analysis")
if agree:
	new_search = search_words
else :
	new_search = search_words + " -filter:retweets"

num = st.sidebar.slider("Number of Tweets", 50, 500)
date_since = "2018-01-01" #year-month-date 

tweets = tw.Cursor(api.search, 
                           q=new_search,
                           lang="en",
                           since=date_since,
                           tweet_mode='extended'
                   ).items(num)

users_locs = [[tweet.created_at, tweet.full_text, TextBlob(tweet.full_text).sentiment.polarity] for tweet in tweets] 

tweet_data = pd.DataFrame(data = users_locs, 
                    columns=["Posted time" ,"Content", "Sentiment"])

pos_count = 0
neg_count = 0
neu_count = 0
for sentiment in tweet_data["Sentiment"] :
        if sentiment < 0 :
            neg_count += 1
        elif sentiment > 0 :
            pos_count += 1
        else :
            neu_count += 1

def senti(sentiment):
  if sentiment < 0 :
    return 'Negative'

  elif sentiment > 0:
    return 'Positive'

  else :
    return 'Neutral'
    
tweet_data['Sentiment'] = tweet_data['Sentiment'].apply(senti)

def clean_tweet(text):
 text = re.sub('@[A-Za-z0–9_]+', '', text)
 text = re.sub('#', '', text)
 text = re.sub('https?:\/\/\S+', '', text) 
 text = re.sub('RT[\s]+', '', text)
 
 return text

tweet_data['Content'] = tweet_data['Content'].apply(clean_tweet)

st.markdown("#### Tweets DataFrame:")
st.dataframe(tweet_data)

st.markdown("#### Quick EDA:")

st.write("Number of Polite Tweets:",pos_count," out of ", num, "live Tweets.")
st.write("Number of Tweets with hate:",neg_count," out of ", num, "live Tweets.")
if neg_count > 0 :
  st.write("Positive vs Negative ratio('Excluding Neutral Comments'): ", pos_count/neg_count)
else :
  st.write("Positive vs Negative ratio('Excluding Neutral Comments'): ", "No Negative Comments")

sns.countplot(x=tweet_data["Sentiment"],data= tweet_data)
st.pyplot()


st.markdown("#### Conclusion:")

st.write("\nSentiment around the topic", search_words,"is :")
if pos_count > neu_count and pos_count > neg_count :
    image = Image.open('Images/happy-face.png')
    st.image(image, caption="Happy",width = 100)

elif neg_count > neu_count and neg_count > pos_count :
    image = Image.open('Images/angry-face.png')
    st.image(image, caption="Sad",width = 100)

else :
    image = Image.open('Images/neutral-face.png')
    st.image(image, caption="Neutral",width = 100)

st.markdown("#### WordCloud:")
all_words = ' '.join([text for text in tweet_data['Content']])
wordcloud = WordCloud(background_color = 'white',width=800, height=500, random_state=21, max_font_size=110).generate(all_words)
fig = plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
st.pyplot(fig)

st.sidebar.title("Info")
st.sidebar.info(
		"This Project uses [Twitter API](https://developer.twitter.com/en) to fetch tweets and related data. \n\n"
		"This project is maintained by [Siddhanth](https://github.com/SiddhanthNB).")
