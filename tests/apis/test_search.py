"""
    tests for search api
"""

import pytest
import responses

import pytwitter


@responses.activate
def test_search_tweets(api, helpers):

    with pytest.raises(pytwitter.PyTwitterError):
        api.search_tweets(query="error", query_type="error")

    tweets_data = helpers.load_json_data(
        "testdata/apis/searches/search_tweets_for_nyc.json"
    )
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/tweets/search/recent",
        json=tweets_data,
    )
    resp = api.search_tweets(
        query="nyc",
        tweet_fields="author_id,created_at,entities,geo,in_reply_to_user_id,lang,possibly_sensitive,referenced_tweets,source",
    )

    assert len(resp.data) == 10
    assert resp.data[0].author_id == "1176828691365736451"

    tweets_data = helpers.load_json_data(
        "testdata/apis/searches/search_tweets_query.json"
    )
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/tweets/search/all",
        json=tweets_data,
    )
    resp = api.search_tweets(
        query="conversation_id:1273733248749690880",
        query_type="all",
        tweet_fields="attachments,author_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,referenced_tweets,source,text,withheld",
        expansions="author_id,referenced_tweets.id",
        user_fields="description,created_at",
    )

    assert len(resp.data) == 4
    assert resp.includes.users[0].id == "63046977"
