## List members lookup
Members lookup group has two available endpoints. You are able to retrieve details on members of a specified List and see which Lists a user is a member of. These endpoints can be used to enable people to curate and organize new Lists based on the membership information.

You can use either [OAuth 1.0a User Context](https://developer.twitter.com/en/docs/authentication/oauth-1-0a) or [OAuth 2.0 Bearer Token](https://developer.twitter.com/en/docs/authentication/oauth-2-0) to authenticate to these endpoints.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/list-members/introduction)

### Get list's members	

Returns a list of users who are members of the specified List.

```python
api.get_list_members(list_id="List ID")
# Response(data=[User(id='1301152652357595137', name='realllkk520', username='realllkk520')])
```

### Get lists for user joined

Returns all Lists a specified user is a member of.

```python
api.get_user_memberships_lists(user_id="User ID")
# Response(data=[TwitterList(id='1402926710174089222', name='🧑🏻\u200d💻 Geeks'), TwitterList(id='1403322685870940160', name='SNS-sdks')])
```


## Manage List members

The manage List members endpoints allow you to add and remove members to a List on behalf of an authenticated user.

For these endpoints, there are two methods available: POST and DELETE. The POST method allows you to add a member to a List, and the DELETE method allows you to remove a member from a List.

You can get more information for this at [docs](https://developer.twitter.com/en/docs/twitter-api/lists/list-members/introduction)

### Add member to a list

Enables the authenticated user to add a member to a List they own.

```python
my_api.add_list_member(list_id="1448302476780871685", user_id="ID for user added to the list")
# {'data': {'is_member': True}}
```

### Remove member from a list

Enables the authenticated user to remove a member from a List they own.

```python
my_api.remove_list_member(list_id="1448302476780871685", user_id="ID for user will be removed from the list")
# {'data': {'is_member': False}}
```
