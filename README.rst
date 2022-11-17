python-twitter

A simple Python wrapper for Twitter API v2 :sparkles: :cake: :sparkles:.

.. image:: https://img.shields.io/endpoint?url=https%3A%2F%2Ftwbadges.glitch.me%2Fbadges%2Fv2
   :target: https://developer.twitter.com/en/docs/twitter-api
   :alt: v2

.. image:: https://github.com/sns-sdks/python-twitter/workflows/Test/badge.svg
    :target: https://github.com/sns-sdks/python-twitter/actions
    :alt: Build Status

.. image:: https://codecov.io/gh/sns-sdks/python-twitter/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/sns-sdks/python-twitter
    :alt: Codecov

.. image:: https://img.shields.io/pypi/v/python-twitter-v2.svg
    :target: https://pypi.org/project/python-twitter-v2/
    :alt: PyPI



============
Introduction
============

Twitter has published new version `Twitter API V2 <https://twitter.com/TwitterDev/status/1293593516040269825>`_ for developer at Aug 13, 2020.

This library provides a service to easily use this new version Twitter API.

=============
Documentation
=============

You can get all API descriptions `Twitter API v2 Documentation <https://developer.twitter.com/en/docs/twitter-api>`_.

Docs for this library on `here <https://sns-sdks.github.io/python-twitter/>`_


==========
Installing
==========

You can install this library easily by `pypi`:

.. code-block:: shell

    $ pip install python-twitter-v2

Code is hosted at `https://github.com/sns-sdks/python-twitter <https://github.com/sns-sdks/python-twitter>`_.

Checkout latest development version with:

.. code-block:: shell

    $ git clone https://github.com/sns-sdks/python-twitter.git
    $ cd python-twitter

Install dependencies with:

.. code-block:: shell

    $ make env


Run tests with:

.. code-block:: shell

    $ make test

Run tests with coverage:

.. code-block:: shell

    $ make cov-term
    $ make cov-html

=====
Using
=====

The API is exposed via the ``pytwitter.Api`` class.

Now covers these features:

- Tweets
    - Tweet lookup
    - Manage Tweets
    - Quote Tweets
    - Timelines
    - Search Tweets
    - Tweet counts
    - Filtered stream
    - Volume streams
    - Retweets
    - Likes
    - Bookmarks
    - Hide replies

- Users
    - User lookup
    - Follows
    - Blocks
    - Mutes

- Spaces
    - Spaces lookup
    - Search Spaces

- Compliance
    - Batch compliance

- Lists
    - List lookup
    - Manage lists
    - List Tweets lookup
    - List members
    - List follows
    - Pinned Lists

- Direct Messages
    - Direct Messages lookup
    - Manage Direct Messages

-----------
INSTANTIATE
-----------

You can initialize with an bearer token:

.. code-block:: python

    >>> from pytwitter import Api
    >>> api = Api(bearer_token="Your bearer token")

With OAuth 1.0A user context token:

.. code-block:: python

    >>> api = Api(
            consumer_key="consumer key",
            consumer_secret="consumer secret",
            access_token="access token",
            access_secret="access secret"
        )

Or with authorization done by user:

.. code-block:: python

    >>> api = Api(consumer_key="consumer key",consumer_secret="consumer secret",oauth_flow=True)
    # get url for user to authorize
    >>> api.get_authorize_url()
    # copy the response url
    >>> api.generate_access_token("https://localhost/?oauth_token=oauth_token&oauth_verifier=oauth_verifier")
    {'oauth_token': 'oauth_token',
     'oauth_token_secret': 'oauth_token_secret',
     'user_id': '123456',
     'screen_name': 'screen name'}

Twitter has `announced OAuth 2.0 user authentication support with fine-grained scopes <https://twittercommunity.com/t/announcing-oauth-2-0-general-availability/163555>`_

Now if you have app with ``OAuth2.0`` client ID. you can do authorize with ``OAuth2``.

.. code-block:: python

    >>> api = Api(client_id="You client ID", oauth_flow=True)
    # get the url and code verifier for user to authorize
    >>> url, code_verifier, _ = api.get_oauth2_authorize_url()
    # copy the response url
    >>> api.generate_oauth2_access_token("https://localhost/?state=state&code=code", code_verifier)
    {'token_type': 'bearer',
     'expires_in': 7200,
     'access_token': 'access_token',
     'scope': 'users.read tweet.read',
     'expires_at': 1631775928}


------------
Users-lookup
------------

You can get information about a user or group of users, specified by a user ID or a username.

Get group of users:

.. code-block:: python

    # By ids
    >>> api.get_users(ids=["783214", "2244994945"])
    Response(data=[User(id='2244994945', name='Twitter Dev', username='TwitterDev'), User(id='783214', name='Twitter', username='Twitter')])

    # By username
    >>> api.get_users(usernames="Twitter,TwitterDev")
    Response(data=[User(id='2244994945', name='Twitter Dev', username='TwitterDev'), User(id='783214', name='Twitter', username='Twitter')])

Get single user:

.. code-block:: python

    # By id
    >>> api.get_user(user_id="783214")
    Response(data=User(id='783214', name='Twitter', username='Twitter'))

    # By username
    >>> api.get_user(username="Twitter")
    Response(data=User(id='783214', name='Twitter', username='Twitter'))

Get user following:

.. code-block:: python

    >>> api.get_following(user_id="2244994945", max_results=5)
    Response(data=[User(id='459860328', name='julie✨', username='JulieMendoza206'), User(id='273830767', name='🄿🅄🅂🄷', username='rahul_pushkarna')...])

Get user followers:

.. code-block:: python

    >>> api.get_followers(user_id="2244994945", max_results=5)
    Response(data=[User(id='715131097332518912', name='Daniel', username='RGIDaniel'), User(id='1176323137757048832', name='Joyce Wang', username='joycew67')...])


You can follow or unfollow user if you have User context.

follow user:

.. code-block:: python

    >>> api.follow_user(user_id="123456", target_user_id="654321")
    {'data': {'following': True, 'pending_follow': False}}


unfollow user:

.. code-block:: python

    >>> api.unfollow_user(user_id="123456", target_user_id="654321")
    {'data': {'following': False}}

-------------
Tweets-lookup
-------------

You can get information about a tweet or group of tweets by tweet id(s).

Get single tweet:

.. code-block:: python

    >>> api.get_tweet("1354143047324299264", expansions=["attachments.media_keys"], media_fields=["type","duration_ms"])
    Response(data=Tweet(id=1354143047324299264, text=Academics are one of the biggest groups using...))

Get group of tweets:

.. code-block:: python

    >>> api.get_tweets(["1261326399320715264","1278347468690915330"],expansions="author_id",tweet_fields=["created_at"], user_fields=["username","verified"])
    Response(data=[Tweet(id=1261326399320715264, text=Tune in to the @MongoDB @Twitch stream...), Tweet(id=1278347468690915330, text=Good news and bad news: 2020 is half over)])

-------------
Streaming API
-------------

For Streaming, this provide `StreamApi` independent. Same as main `Api`, You need initialize it first.

.. code-block:: python

    >>> from pytwitter import StreamApi
    >>> stream_api = StreamApi(bearer_token="bearer token")
    # or use consumer key and secret
    >>> stream_api = StreamApi(consumer_key="consumer key", consumer_secret="consumer secret")


For Sample Stream tweets, you can use the `sample_stream` function to build a connection.

.. code-block:: python

    >>> stream_api.sample_stream()

For Filtered Stream, you can create rules.

Get your current rules.

.. code-block:: python

    >>> stream_api.get_rules()
    Response(data=[StreamRule(id='1369580714056843266', value='twitter api ')])

Delete your rules.

.. code-block:: python

    >>> stream_api.manage_rules(rules={"delete": {"ids": ["1369580714056843266"]}})
    Response(data=[])

Add new rules. If you set `dry_run` to True, will only validate rules, and not create them.

.. code-block:: python

    >>> np = {
            "add": [
                {"value": "cat has:media", "tag": "cats with media"},
                {"value": "cat has:media -grumpy", "tag": "happy cats with media"}
            ]
         }
    >>> stream_api.manage_rules(rules=np, dry_run=True)
    Response(data=[StreamRule(id='1370406958721732610', value='cat has:media -grumpy'), StreamRule(id='1370406958721732609', value='cat has:media')])

Then you can use `search_stream` to get tweets matching your rules.

.. code-block:: python

    >>> stream_api.search_stream()


You can go to the `Example folder <examples>`_ for streaming examples.

====
TODO
====

- More Api waiting twitter

