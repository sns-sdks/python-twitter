"""
    tests for stream
"""
import json
import random
from unittest.mock import patch

import pytest
import responses

from pytwitter import StreamApi, PyTwitterError


class MyStreamApi(StreamApi):
    def __init__(
        self,
        bearer_token=None,
        consumer_key=None,
        consumer_secret=None,
        proxies=None,
        max_retries=3,
        timeout=None,
        chunk_size=1024,
    ):
        super().__init__(
            bearer_token=bearer_token,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            proxies=proxies,
            max_retries=max_retries,
            timeout=timeout,
            chunk_size=chunk_size,
        )

        self.tweet_max_count = 10
        self.tweet_count = 0

    def on_tweet(self, tweet):
        self.tweet_count += 1

        if self.tweet_count >= self.tweet_max_count:
            self.disconnect()


def test_stream_running():
    with pytest.raises(PyTwitterError):
        api = StreamApi(bearer_token="bearer token")
        api.running = True
        api.sample_stream()

    with pytest.raises(PyTwitterError):
        api = StreamApi(bearer_token="bearer token")
        api.running = True
        api.search_stream()


@responses.activate
def test_stream_connect():
    tweet_data = {
        "data": {
            "id": "1067094924124872705",
            "text": "Just getting started with Twitter APIs?",
        }
    }

    def callback(request):
        s = random.randint(1, 2)
        if s == 1:
            return 200, {}, json.dumps(tweet_data)
        else:
            return 200, {}, "\r\n"

    responses.add(
        responses.CallbackResponse(
            responses.GET,
            url="https://api.twitter.com/2/tweets/sample/stream",
            callback=callback,
            stream=True,
            content_type="application/json",
        )
    )

    stream_api = MyStreamApi(bearer_token="bearer token")

    stream_api.sample_stream()

    assert stream_api.running == False
    assert stream_api.tweet_max_count == 10


@responses.activate
@patch("time.sleep", return_value=None)
def test_stream_error(patched_time_sleep):
    responses.add(
        responses.Response(
            responses.GET,
            url="https://api.twitter.com/2/tweets/search/stream",
            stream=True,
            content_type="application/json",
            status=400,
        )
    )

    api = StreamApi(bearer_token="bearer token", max_retries=10)
    api.search_stream()
