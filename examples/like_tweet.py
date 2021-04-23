"""
    A demo for like tweet.
"""

from pytwitter import Api

consumer_key = "your app consumer key"
consumer_secret = "your app consumer secret"

api = Api(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    oauth_flow=True,
)

authorize_url = api.get_authorize_url()
print(f"Click authorize url to do authorize: {authorize_url}")

resp = input("Response here: ")

token = api.generate_access_token(response=resp)
print(f"Get token: {token}")
# Get token: {'oauth_token': 'token', 'oauth_token_secret': 'token_secret', 'user_id': 'user_id', 'screen_name': 'name'}

user_id = input("Your user id: ")
tweet_id = input("Tweet id you want to like:")

resp = api.like_tweet(
    user_id=user_id,
    tweet_id=tweet_id,
)
print(f"Resp: {resp}")
# Resp: {'data': {'liked': True}}
