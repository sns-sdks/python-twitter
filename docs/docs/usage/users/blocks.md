The manage blocks endpoints enable you to block or unblock a specified user on behalf of an authenticated user.

For this endpoint group, there are two methods available POST and DELETE. The POST method allows you to block a user, and the DELETE method will enable you to unblock.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/users/blocks/introduction)

## Blocks

You can block a user

```python
my_api.block_user(user_id=my_api.auth_user_id, target_user_id="target user id")
# {'data': {'blocking': True}}
```

Unblock a user

```python
my_api.unblock_user(user_id=my_api.auth_user_id, target_user_id="target user id")
# {'data': {'blocking': False}}
```
