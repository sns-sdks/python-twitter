List Tweets lookup has one available endpoint to retrieve Tweets from a specified List. With this endpoint, you can build solutions that enable users to customize, organize and prioritize the Tweets they see in their timeline.

You can use either [OAuth 1.0a User Context](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) or [OAuth 2.0 Bearer Token](https://developer.twitter.com/en/docs/authentication/oauth-2-0) to authenticate to these endpoints. If you choose to use [OAuth 1.0a User Context](https://developer-staging.twitter.com/en/docs/authentication/oauth-1-0a), use the Access Tokens associated with a user that has authorized your App. You can generate Access Tokens using the [3-legged OAuth flow](https://developer-staging.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens).

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/list-tweets/introduction)

## Lookup Tweets from a specified List

Returns a list of Tweets from the specified List.

```python
api.get_list_tweets("1403322685870940160")
# Response(data=[Tweet(id=1458088293904654340, text=Simple tweet from python-twitter-v2....), Tweet(id=1301154770489499650, text=Hey this is new begin.)])
```
