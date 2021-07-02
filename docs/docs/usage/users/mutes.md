The manage mute endpoints enable you to mute or unmute a specified account on behalf of an authenticated user.

For these endpoints, there are two methods available: POST and DELETE. The POST method allows you to mute an account, and the DELETE method allows you to unmute an account. There is a user rate limit of 50 requests per 15 minutes for both the POST and DELETE endpoints.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/users/mutes/introduction)

## Mutes

You can mute a user

```python
my_api.mute_user(user_id=my_api.auth_user_id, target_user_id="target user id")
# {'data': {'muting': True}}
```

Unmute a user

```python
my_api.unmute_user(user_id=my_api.auth_user_id, target_user_id="target user id")
# {'data': {'muting': False}}
```
