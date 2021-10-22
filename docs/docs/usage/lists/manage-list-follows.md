The manage List follows endpoints allow you to follow and unfollow a List on behalf of an authenticated user.

For these endpoints, there are two methods available: POST and DELETE. The POST method allows you to follow a List, and the DELETE method allows you to delete a List.

There is a user rate limit of 50 requests per 15 minutes for both endpoints.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/post-users-id-followed-lists)

## Follow a list

```python
my_api.follow_list(user_id=my_api.auth_user_id, list_id="1448302476780871685")
# {'data': {'following': True}}
```

## Unfollow a list

```python
my_api.unfollow_list(user_id=my_api.auth_user_id, list_id="1448302476780871685")
# {'data': {'following': False}}
```
