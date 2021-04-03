
Twitter allow app to lookup users. You can get more information at [Lookup docs](https://developer.twitter.com/en/docs/twitter-api/users/lookup/introduction).

If you have the username or ID for user(s) which you want to get data. You can use follows methods:

Get multiple users by one requests

```python
# Get by ids
api.get_users(ids=["783214", "2244994945"])
# Response(data=[User(id='2244994945', name='Twitter Dev', username='TwitterDev'), User(id='783214', name='Twitter', username='Twitter')])

# Get by usernames
api.get_users(usernames="Twitter,TwitterDev")
# Response(data=[User(id='2244994945', name='Twitter Dev', username='TwitterDev'), User(id='783214', name='Twitter', username='Twitter')])
```

Get one user:

```python
# By id
api.get_user(user_id="783214")
# Response(data=User(id='783214', name='Twitter', username='Twitter'))

# By username
api.get_user(username="Twitter")
# Response(data=User(id='783214', name='Twitter', username='Twitter'))
```
