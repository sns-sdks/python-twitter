python-twitter

A simple Python wrapper around for Twitter API v2 :sparkles: :cake: :sparkles:.

.. image:: https://github.com/sns-sdks/python-twitter/workflows/Test/badge.svg
    :target: https://github.com/sns-sdks/python-facebook/actions
    :alt: Build Status


============
Introduction
============

Twitter has published new version `Twitter API V2 <https://twitter.com/TwitterDev/status/1293593516040269825>`_ for developer at Aug 13, 2020.

This library provides a service to easily use this new version Twitter API.

=============
Documentation
=============

You can get all api description and update at `Twitter API v2: Early Access <https://developer.twitter.com/en/docs/twitter-api/early-access>`_.


==========
Installing
==========

TODO not published.

=====
Using
=====

The API is exposed via the ``pytwitter.Api`` class.

-----------
INSTANTIATE
-----------

You can initialize with an bearer token::


    In[1]: from pytwitter import Api
    In[2]: api = Api(bearer_token="You bearer token")


------------
Users-lookup
------------

You can get information about a user or group of users, specified by a user ID or a username.

Get group of users::

    # By ids
    In[3]: api.get_users(ids=["783214", "2244994945"])
    Out[3]:
    ([User(id='783214', name='Twitter', username='Twitter'),
      User(id='2244994945', name='Twitter Dev', username='TwitterDev')],
     None)

    # By username
    In[4]: api.get_users(usernames="Twitter,TwitterDev")
    Out[4]:
    ([User(id='783214', name='Twitter', username='Twitter'),
      User(id='2244994945', name='Twitter Dev', username='TwitterDev')],
     None)

Get single user::

    # By id
    In[5]: api.get_user(user_id="783214")
    Out[5]: (User(id='783214', name='Twitter', username='Twitter'), None)

    # By username
    In[6]: api.get_user(username="Twitter")
    Out[6]: (User(id='783214', name='Twitter', username='Twitter'), None)

====
TODO
====

- Tweet
- Pypi
