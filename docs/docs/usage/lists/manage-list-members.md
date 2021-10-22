The manage List members endpoints allow you to add and remove members to a List on behalf of an authenticated user.

For these endpoints, there are two methods available: POST and DELETE. The POST method allows you to add a member to a List, and the DELETE method allows you to remove a member from a List. 

There is a user rate limit of 300 requests per 15 minutes for both endpoints.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/post-lists-id-members)

## Add member to a list

```python
my_api.add_list_member(list_id="1448302476780871685", user_id="ID for user added to the list")
# {'data': {'is_member': True}}
```

## Remove member from a list

```python
my_api.remove_list_member(list_id="1448302476780871685", user_id="ID for user will be removed from the list")
# {'data': {'is_member': False}}
```
