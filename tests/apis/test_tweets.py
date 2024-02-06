"""
    tests for tweet api
"""

import pytest
import responses
from pytwitter import PyTwitterError


@responses.activate
def test_get_tweet(api, helpers):
    tweet_data = helpers.load_json_data("testdata/apis/tweet/tweet_resp.json")
    tweet_id = "1067094924124872705"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}",
        json=tweet_data,
    )

    resp = api.get_tweet(
        tweet_id=tweet_id,
        expansions="attachments.media_keys",
        media_fields=["type", "duration_ms"],
    )
    assert resp.data.id == tweet_id
    assert resp.data.attachments.media_keys[0] == "13_1064638969197977600"
    assert resp.includes.media[0].type == "video"

    resp_json = api.get_tweet(
        tweet_id=tweet_id,
        expansions="attachments.media_keys",
        media_fields=("type", "duration_ms"),
        return_json=True,
    )
    assert resp_json["data"]["id"] == tweet_id
    assert resp_json["data"]["attachments"]["media_keys"][0] == "13_1064638969197977600"
    assert resp_json["includes"]["media"][0]["duration_ms"] == 136637


@responses.activate
def test_get_tweets(api, helpers):
    tweets_data = helpers.load_json_data("testdata/apis/tweet/tweets_resp.json")
    tweet_ids = ["1261326399320715264", "1278347468690915330"]

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets",
        json=tweets_data,
    )

    resp = api.get_tweets(
        tweet_ids=tweet_ids,
        expansions=["author_id"],
        tweet_fields="created_at",
        user_fields=["username", "verified"],
    )
    assert len(resp.data) == 2
    assert resp.data[0].id in tweet_ids
    assert resp.includes.users[0].verified

    resp_json = api.get_tweets(
        tweet_ids="1261326399320715264,1278347468690915330",
        expansions="author_id",
        tweet_fields=["created_at"],
        user_fields="username,verified",
        return_json=True,
    )
    assert resp_json["data"][0]["id"] in tweet_ids
    assert resp_json["includes"]["users"][0]["id"] == "2244994945"


@responses.activate
def test_like_and_unlike_tweet(api_with_user):
    user_id, tweet_id = "123456", "10987654321"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/likes",
        json={"data": {"liked": True}},
    )

    resp = api_with_user.like_tweet(user_id=user_id, tweet_id=tweet_id)
    assert resp["data"]["liked"]

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/likes/{tweet_id}",
        json={"data": {"liked": False}},
    )

    resp = api_with_user.unlike_tweet(user_id=user_id, tweet_id=tweet_id)
    assert not resp["data"]["liked"]


@responses.activate
def test_tweet_liking_users(api, helpers):
    tweets_data = helpers.load_json_data(
        "testdata/apis/tweet/tweet_liking_users_resp.json"
    )
    tweet_id = "1395447825366847488"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/liking_users",
        json=tweets_data,
    )

    resp = api.get_tweet_liking_users(
        tweet_id=tweet_id,
        expansions=["author_id"],
        tweet_fields=["created_at"],
        user_fields=["created_at"],
    )
    assert len(resp.data) == 4
    assert resp.data[0].id == "1000247636354461697"
    assert resp.includes.tweets[0].id == "1383963809702846470"

    resp_json = api.get_tweet_liking_users(
        tweet_id=tweet_id,
        expansions="author_id",
        tweet_fields="created_at",
        user_fields="created_at",
        return_json=True,
    )
    assert resp_json["data"][0]["id"] == "1000247636354461697"
    assert resp_json["includes"]["tweets"][0]["id"] == "1383963809702846470"


@responses.activate
def test_get_user_bookmarks(api_with_user, helpers):
    user_id = "2244994945"
    tweets_data = helpers.load_json_data(
        "testdata/apis/tweet/tweets_by_user_bookmark.json"
    )
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/bookmarks",
        json=tweets_data,
    )

    resp = api_with_user.get_bookmark_tweets(
        user_id=user_id,
        max_results=5,
        expansions="attachments.media_keys",
        media_fields="type,duration_ms",
    )
    assert len(resp.data) == 5
    assert resp.data[0].id == "1362449997430542337"


@responses.activate
def test_user_bookmark_tweet_or_remove_tweet(api_with_user):
    user_id, tweet_id = "2244994945", "1228393702244134912"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/bookmarks",
        json={"data": {"bookmarked": True}},
    )

    resp = api_with_user.bookmark_tweet(user_id=user_id, tweet_id=tweet_id)
    assert resp["data"]["bookmarked"]

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/bookmarks/{tweet_id}",
        json={"data": {"bookmarked": False}},
    )

    resp = api_with_user.bookmark_tweet_remove(user_id=user_id, tweet_id=tweet_id)
    assert not resp["data"]["bookmarked"]


@responses.activate
def test_get_tweet_quote_tweets(api, helpers):
    tweets_data = helpers.load_json_data(
        "testdata/apis/tweet/tweet_quote_tweets_resp.json"
    )
    tweet_id = "1409931481552543749"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/quote_tweets",
        json=tweets_data,
    )

    resp = api.get_tweet_quote_tweets(
        tweet_id=tweet_id,
        expansions=["author_id"],
        tweet_fields=[
            "created_at",
            "author_id",
            "conversation_id",
            "public_metrics",
            "context_annotations",
        ],
        user_fields=["username"],
        max_results=15,
    )
    assert len(resp.data) == 15
    assert resp.data[0].id == "1495979553889697792"
    assert resp.includes.users[0].id == "29757971"


@responses.activate
def test_get_tweet_retweeted_tweets(api, helpers):
    tweets_data = helpers.load_json_data(
        "testdata/apis/tweet/tweet_retweet_tweets_resp.json"
    )
    tweet_id = "1720506615714213927"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/retweets",
        json=tweets_data,
    )

    resp = api.get_tweet_retweeted_tweets(
        tweet_id=tweet_id,
        expansions=["author_id"],
        tweet_fields=[
            "created_at",
            "author_id",
            "conversation_id",
            "public_metrics",
        ],
        user_fields=[
            "id",
            "name",
            "username",
            "created_at",
        ],
        max_results=10,
    )
    assert len(resp.data) == 8
    assert resp.data[0].id == "1724975633908789418"
    assert resp.includes.users[0].id == "1220870789794353155"


@responses.activate
def test_get_tweets_count(api, helpers):
    recent_counts_data = helpers.load_json_data(
        "testdata/apis/tweet/tweets_counts_recent_resp.json"
    )
    all_counts_data = helpers.load_json_data(
        "testdata/apis/tweet/tweets_counts_all_resp.json"
    )

    with pytest.raises(PyTwitterError):
        api.get_tweets_counts(query="A", search_type="B")

    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/tweets/counts/recent",
        json=recent_counts_data,
    )
    resp = api.get_tweets_counts(
        query="lakers",
    )
    assert len(resp.data) == 169
    assert resp.data[0].tweet_count == 345
    assert resp.meta.total_tweet_count == 744364

    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/tweets/counts/all",
        json=all_counts_data,
    )
    resp_json = api.get_tweets_counts(
        query="lakers",
        search_type="all",
        granularity="day",
        start_time="2020-01-01T00%3A00%3A00Z",
        end_time="2020-01-15T00%3A00%3A00Z",
        return_json=True,
    )

    assert len(resp_json["data"]) == 14
    assert resp_json["data"][0]["tweet_count"] == 18392


@responses.activate
def test_tweet_retweeted_users(api, helpers):
    tweets_data = helpers.load_json_data(
        "testdata/apis/tweet/tweet_retweed_users_resp.json"
    )
    tweet_id = "1354143047324299264"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/retweeted_by",
        json=tweets_data,
    )

    resp = api.get_tweet_retweeted_users(
        tweet_id=tweet_id,
        user_fields=["created_at"],
        expansions=["pinned_tweet_id"],
        tweet_fields=["created_at"],
    )
    assert len(resp.data) == 5
    assert resp.data[0].id == "1065249714214457345"
    assert resp.meta.result_count == 5
    assert resp.includes.tweets[0].id == "1389270063807598594"


@responses.activate
def test_retweet_remove_retweet_tweet(api_with_user, helpers):
    uid, tweet_id = "123456", "1228393702244134912"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{uid}/retweets",
        json={"data": {"retweeted": True}},
    )

    resp = api_with_user.retweet_tweet(user_id=uid, tweet_id=tweet_id)
    assert resp["data"]["retweeted"]

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{uid}/retweets/{tweet_id}",
        json={"data": {"retweeted": False}},
    )

    resp = api_with_user.remove_retweet_tweet(user_id=uid, tweet_id=tweet_id)
    assert not resp["data"]["retweeted"]


@responses.activate
def test_create_tweet(api_with_user, helpers):
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/tweets",
        json=helpers.load_json_data("testdata/apis/tweet/create_tweet_resp.json"),
    )

    resp = api_with_user.create_tweet(text="Hello world!")
    assert resp.id == "1445880548472328192"

    resp = api_with_user.create_tweet(
        direct_message_deep_link="https://twitter.com/messages/compose?recipient_id=2244994945",
        for_super_followers_only=True,
        geo_place_id="5a110d312052166f",
        media_media_ids=["1455952740635586573"],
        media_tagged_user_ids=["2244994945", "6253282"],
        poll_duration_minutes=120,
        poll_options=["yes", "maybe", "no"],
        quote_tweet_id="1455953449422516226",
        reply_in_reply_to_tweet_id="1455953449422516226",
        reply_exclude_reply_user_ids=["6253282"],
        reply_settings="mentionedUsers",
        return_json=True,
    )
    assert resp["data"]["id"] == "1445880548472328192"


@responses.activate
def test_delete_tweet(api_with_user, helpers):
    tweet_id = "1445880548472328192"

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}",
        json={"data": {"deleted": True}},
    )

    resp = api_with_user.delete_tweet(tweet_id=tweet_id)
    assert resp["data"]["deleted"]
