The manage pinned List endpoints allow you to pin and unpin a List on behalf of an authenticated user.

For these endpoints, there are two methods available: POST and DELETE. The POST method allows you to pin a List, and the DELETE method allows you to unpin a List.

There is a user rate limit of 50 requests per 15 minutes for both endpoints.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/post-users-id-pinned-lists)

## Pin a list

```python
my_api.pin_list(user_id=my_api.auth_user_id, list_id="ID for list to pin")
# {'data': {'pinned': True}}
```

## Unpin a list

```python
my_api.unpin_list(user_id=my_api.auth_user_id, list_id="ID for list to unpin")
# {'data': {'pinned': False}}
```
