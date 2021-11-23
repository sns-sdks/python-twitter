## Manage pinned Lists

The manage pinned List endpoints allow you to pin and unpin a List on behalf of an authenticated user.

For these endpoints, there are two methods available: POST and DELETE. The POST method allows you to pin a List, and the DELETE method allows you to unpin a List.

There is a user rate limit of 50 requests per 15 minutes for both endpoints.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/pinned-lists/introduction)

### Pin a list

Enables the authenticated user to pin a List.

```python
my_api.pin_list(user_id=my_api.auth_user_id, list_id="ID for list to pin")
# {'data': {'pinned': True}}
```

### Unpin a list

Enables the authenticated user to unpin a List.

```python
my_api.unpin_list(user_id=my_api.auth_user_id, list_id="ID for list to unpin")
# {'data': {'pinned': False}}
```

## Pinned List lookup

Pinned List lookup has one available endpoint that allows you to retrieve an authenticated user's pinned Lists. There is a rate limit of 15 requests per 15 minutes for this endpoint.

Since you are making requests on behalf of a user with all pinned List endpoints, you must authenticate with [OAuth 1.0a User Context](https://developer-staging.twitter.com/en/docs/authentication/oauth-1-0a) and use the Access Tokens associated with a user that has authorized your App.  You can generate Access Tokens using the [3-legged OAuth flow](https://developer-staging.twitter.com/en/docs/authentication/oauth-1-0a/obtaining-user-access-tokens).

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/pinned-lists/introduction)

### Get user pinned lists

Returns the Lists pinned by a specified user.

```python
my_api.get_user_pinned_lists(user_id=my_api.auth_user_id)
# Response(data=[TwitterList(id='1403322685870940160', name='SNS-sdks')])
```
