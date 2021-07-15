The manage Likes endpoints enable you to like or unlike a specified Tweet on behalf of an authenticated account. 

For this endpoint group, there are two methods available POST and DELETE. The POST method allows you to like a Tweet, and the DELETE method will enable you to unlike a Tweet.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/tweets/likes/introduction)

## likes

You can like a tweet

```python
my_api.like_tweet(user_id=my_api.auth_user_id, tweet_id="target tweet id")
# {'data': {'liked': True}}
```

Unlike a tweet

```python
my_api.unlike_tweet(user_id=my_api.auth_user_id, tweet_id="target tweet id")
# {'data': {'liked': False}}
```

## Liking users

You can get users who are liking the tweet

```python
api.get_tweet_liking_users(tweet_id="1395803619614679041")
```

## liked tweets

You can get tweets which are liking by you.

```python
api.get_user_liked_tweets(user_id=my_api.auth_user_id)
```