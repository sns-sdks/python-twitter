python-twitter

A simple Python wrapper around for Twitter API v2 :sparkles: :cake: :sparkles:.

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

You can get all api description and update at `Twitter API v2: Early Access <https://developer.twitter.com/en/docs/twitter-api/early-access>`_.

Library docs site on `here <https://sns-sdks.github.io/python-twitter/>`_


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

-----------
INSTANTIATE
-----------

You can initialize with an bearer token:

.. code-block:: python

    >>> from pytwitter import Api
    >>> api = Api(bearer_token="You bearer token")

With user context token:

.. code-block:: python

    >>> api = Api(
            consumer_key="consumer key",
            consumer_secret="consumer secret",
            access_token="access token",
            access_secret="access secret"
        )

Or with authorize by user:

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


You can follow or unfollow user if you have OAuth 1.0a User context.

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

---------
Timelines
---------

You can get target user timeline tweets by user id.

Get timelines:

.. code-block:: python

    >>> api.get_timelines(user_id="2244994945")
    Response(data=[Tweet(id=1364275610764201984, text=If you're newly approved for the Academic...), Tweet(id=1362876655061073928, text=From our living rooms to yours 🐱‍💻🛋️Our...), Tweet(id=1362439338978467841, text=“To quote my creator Jerome Gangneux, I always...), Tweet(id=1362439338169016324, text=“In the 20th century, managers managed humans,...), Tweet(id=1362439336910675970, text=Meet one of the useful Twitter bots out there:...), Tweet(id=1359912509940011010, text=Valentine’s Day is approaching! 💙 Over the...), Tweet(id=1359554366051504129, text=Go ahead, follow another puppy account. We...), Tweet(id=1357371424487268354, text=Learn how academics can get historical Tweets...), Tweet(id=1356991771553583106, text=Who knew an API could be delicious?...), Tweet(id=1354215875998437376, text=RT @TwitterOSS: Today we’re happy to share...)])

You can get tweets which mention target user by user id.

Get mention tweets:

.. code-block:: python

    >>> api.get_mentions(user_id="2244994945")
    Response(data=[Tweet(id=1364407587207213056, text=@scottmathson @TwitterDev What would you want...), Tweet(id=1364398068313903104, text=@Twitter should consider supporting...), Tweet(id=1364377794327633925, text=@sugan2424 @TwitterDev @threadreaderapp You...), Tweet(id=1364377404156772352, text=@TwitterDev What kind of tweet / attachment is...), Tweet(id=1364373969852366849, text=• Thirdly, that @Twitter, @Twittersafety,...), Tweet(id=1364367885582352386, text=@Twitter @TwitterSafety @TwitterDev @jack...), Tweet(id=1364366114998870016, text=I have mixed feelings about @Twitter /...), Tweet(id=1364364744916951040, text=@Casanovacane @jack @TwitterDev can we get a...), Tweet(id=1364359199795240961, text=@TwitterDev @suhemparack A Blue app going to...), Tweet(id=1364338409494503425, text=@FairyMaitre @TwitterDev tkt)])

-------------
Search Tweets
-------------

Search tweets has two type. For standard project, you can use recent api to search tweets from the last seven days.
If you have `Academic Research Project <https://developer.twitter.com/en/docs/projects/overview>`_, you can use full-archive
api with query type all.

Search by recent tweets:

.. code-block:: python

    >>> api.search_tweets(query="python")
    Response(data=[Tweet(id=1364512148865564675, text=RT @jesss_codes: Your resume: Git SSL Vue CSS...), Tweet(id=1364512106385702914, text=RT @theweeflea: Sturgeon goes on TV to declare...), Tweet(id=1364512102606467074, text=RT @tkEzaki:...), Tweet(id=1364512092343070721, text=RT @ore57436902: #Python #pyxel #ドルアーガの塔...), Tweet(id=1364512076601856007, text=RT @shosen_bt_pc:...), Tweet(id=1364512071866605568, text=RT @CatherineAdenle: 6 ways learning coding can...), Tweet(id=1364512071614889987, text=RT @giswqs: #geemap v0.8.11 has been released....), Tweet(id=1364512066770509824, text=RT @Akpanannang: Today when coming out from the...), Tweet(id=1364512053252284419, text=RT @HarbRimah: New Off-the-Shelf (OTS) Datasets...), Tweet(id=1364512030800171011, text=RT @gzadkowski: Day 5 - #100DaysOfCode...)])


Search by full-archive tweets:

.. code-block:: python

    >>> api.search_tweets(query="python", query_type="all")
    Response(data=[Tweet(id=1364512148865564675, text=RT @jesss_codes: Your resume: Git SSL Vue CSS...), Tweet(id=1364512106385702914, text=RT @theweeflea: Sturgeon goes on TV to declare...), Tweet(id=1364512102606467074, text=RT @tkEzaki:...), Tweet(id=1364512092343070721, text=RT @ore57436902: #Python #pyxel #ドルアーガの塔...), Tweet(id=1364512076601856007, text=RT @shosen_bt_pc:...), Tweet(id=1364512071866605568, text=RT @CatherineAdenle: 6 ways learning coding can...), Tweet(id=1364512071614889987, text=RT @giswqs: #geemap v0.8.11 has been released....), Tweet(id=1364512066770509824, text=RT @Akpanannang: Today when coming out from the...), Tweet(id=1364512053252284419, text=RT @HarbRimah: New Off-the-Shelf (OTS) Datasets...), Tweet(id=1364512030800171011, text=RT @gzadkowski: Day 5 - #100DaysOfCode...)])

----------
Hide reply
----------

This api need user OAuth 1.0a User context.

You can hide reply tweet which belong to a conversation initiated by you.

.. code-block:: python

    >>> api.hidden_reply(tweet_id="tweet id")

You can unhide a reply tweet by api:

.. code-block:: python

    >>> api.hidden_reply(tweet_id="tweet id", hidden=False)

-------------
Streaming API
-------------

For Streaming, this provide `StreamApi` independent. Same as main `Api`, You need initial it first.

.. code-block:: python

    >>> from pytwitter import StreamApi
    >>> stream_api = StreamApi(bearer_token="bearer token")
    # or use consumer key and secret
    >>> stream_api = StreamApi(consumer_key="consumer key", consumer_secret="consumer secret")


For Sample Stream tweets, You can use `sample_stream` function to build a connection.

.. code-block:: python

    >>> stream_api.sample_stream()

For Search Stream, You can point your rules.

Get your current rules.

.. code-block:: python

    >>> stream_api.get_rules()
    Response(data=[StreamRule(id='1369580714056843266', value='twitter api ')])

Delete You rules.

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

Then you can use `search_stream` to get tweets match your rules.

.. code-block:: python

    >>> stream_api.search_stream()


You can go to the `Example folder <examples>`_ for streaming examples.

====
TODO
====

- More Api waiting twitter

