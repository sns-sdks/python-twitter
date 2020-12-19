python-twitter

A simple Python wrapper around for Twitter API v2 :sparkles: :cake: :sparkles:.

.. image:: https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fv2
   :target: https://developer.twitter.com/en/docs/twitter-api
   :alt: v2

.. image:: https://github.com/sns-sdks/python-twitter/workflows/Test/badge.svg
    :target: https://github.com/sns-sdks/python-facebook/actions
    :alt: Build Status

.. image:: https://codecov.io/gh/sns-sdks/python-twitter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/sns-sdks/python-facebook
    :alt: Codecov

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

Code is hosted at `https://github.com/sns-sdks/python-twitter <https://github.com/sns-sdks/python-twitter>`_.

Checkout latest development version with::

    $ git clone https://github.com/sns-sdks/python-twitter.git
    $ cd python-twitter

Install dependencies with::

    $ make env


Run tests with::

    $ make test

Run tests with coverage::

    $ make cov-term
    $ make cov-html


TODO pypi not published will come soon.

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


-------------
Tweets-lookup
-------------

You can get information about a tweet or group of tweets by tweet id(s).

Get single tweet::

    In[7]: api.get_tweet("1067094924124872705", expansions=["attachments.media_keys"], media_fields=["type","duration_ms"])
    Out[7]:
    (Tweet(id=1067094924124872705, text=Just getting started with Twitter APIs? Find...),
     Includes(media=[Media(media_key='13_1064638969197977600', type='video')], places=None, polls=None, tweets=None, users=None))

Get group of tweets::

    In[8]: api.get_tweets(["1261326399320715264","1278347468690915330"],expansions="author_id",tweet_fields=["created_at"], user_fields=["username","verified"])
    Out[8]:
    ([Tweet(id=1261326399320715264, text=Tune in to the @MongoDB @Twitch stream...),
      Tweet(id=1278347468690915330, text=Good news and bad news: 2020 is half over)],
     Includes(media=None, places=None, polls=None, tweets=None, users=[User(id='2244994945', name='Twitter Dev', username='TwitterDev'), User(id='783214', name='Twitter', username='Twitter')]))


====
TODO
====

- Tweet
- Pypi
