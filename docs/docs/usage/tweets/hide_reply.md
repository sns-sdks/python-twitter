This endpoint gives you the ability to programmatically hide or unhide replies using criteria you define.

hide reply

```python
my_api.hidden_reply(tweet_id="tweet id")
# {"data":{"hidden":true}}
```

un-hide reply

```python
my_api.hidden_reply(tweet_id="tweet id", hidden=False)
# {"data":{"hidden":false}}
```
