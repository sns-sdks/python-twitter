"""
    Api for streaming.
"""
import base64
import json
import logging
import time

import requests
import pytwitter.models as md
from pytwitter.error import PyTwitterError
from requests_oauthlib.oauth2_auth import OAuth2

logger = logging.getLogger(__name__)


class StreamApi:
    BASE_URL = "https://api.twitter.com/2"

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
        self.running = False
        self._auth = None
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.proxies = proxies
        self.session = requests.Session()
        self.max_retries = max_retries
        self.timeout = timeout
        self.chunk_size = chunk_size

        if bearer_token:
            self._auth = OAuth2(
                token={"access_token": bearer_token, "token_type": "Bearer"}
            )
        elif all([self.consumer_key, self.consumer_secret]):
            resp = self.generate_bearer_token(
                consumer_key=consumer_key, consumer_secret=consumer_secret
            )
            self._auth = OAuth2(
                token={"access_token": resp["access_token"], "token_type": "Bearer"}
            )
        else:
            raise PyTwitterError("Need oauth")

    @staticmethod
    def generate_bearer_token(consumer_key: str, consumer_secret: str) -> dict:
        """
        :param consumer_key: Your app consumer key
        :param consumer_secret: Your app consumer secret
        :return: token data
        """
        bearer_token = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode())
        headers = {
            "Authorization": f"Basic {bearer_token.decode()}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        resp = requests.post(
            url="https://api.twitter.com/oauth2/token",
            data={"grant_type": "client_credentials"},
            headers=headers,
        )

        data = resp.json()
        if "errors" in data:
            raise PyTwitterError(data["errors"])
        return data

    def _connect(self, url, params=None, return_json=False):
        """
        :param url:
        :param params:
        :param return_json:
        :return:
        """
        if not self._auth:
            raise PyTwitterError("Need auth")
        # make sure only one running connect
        self.running = True
        retries = 0
        http_error_wait = 5
        http_error_wait_max = 320

        try:
            while self.running and retries < self.max_retries:
                with self.session.get(
                    url=url,
                    params=params,
                    auth=self._auth,
                    proxies=self.proxies,
                    timeout=self.timeout,
                    stream=True,
                ) as resp:
                    if resp.status_code == 200:
                        print(resp.headers)
                        for line in resp.iter_lines(chunk_size=self.chunk_size):
                            if line:
                                self.on_data(raw_data=line, return_json=return_json)
                            else:
                                self.on_keep_alive()
                            if not self.running:
                                break
                    else:
                        self.on_request_error(resp.status_code)
                        retries += 1
                        time.sleep(http_error_wait)

                        http_error_wait *= 2
                        if http_error_wait > http_error_wait_max:
                            break
        except Exception as exc:
            logger.exception(f"Exception in request, exc: {exc}")
        finally:
            self.session.close()
            self.running = False

    def disconnect(self):
        self.running = False

    def on_data(self, raw_data, return_json=False):
        """
        :param raw_data: Response data by twitter api.
        :param return_json:
        :return:
        """
        data = json.loads(raw_data)
        if "errors" in data:
            raise PyTwitterError(data["errors"])

        if return_json:
            data = md.Tweet.new_from_json_dict(data=data["data"])

        return self.on_tweet(tweet=data)

    def on_tweet(self, tweet):
        """
        :param tweet: Tweet obj or json data.
        :return:
        """
        print(f"Received tweet: {tweet}")

    def on_keep_alive(self):
        """
        Refer: https://developer.twitter.com/en/docs/twitter-api/tweets/sampled-stream/integrate/handling-disconnections
        :return:
        """
        logger.debug("Received keep alive signal")

    def on_request_error(self, status_code):
        logger.debug(f"Received error status code: {status_code}")
