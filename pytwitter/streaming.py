"""
    Api for streaming.
"""
import base64
import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Union

import requests
import pytwitter.models as md
from pytwitter.error import PyTwitterError
from pytwitter.utils.validators import enf_comma_separated
from requests.models import Response
from authlib.integrations.requests_client import OAuth2Auth

logger = logging.getLogger(__name__)


class StreamApi:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        proxies: Optional[dict] = None,
        max_retries: int = 3,
        timeout: Optional[int] = None,
        chunk_size: int = 1024,
    ) -> None:
        """
        :param bearer_token: Access token for app or user.
        :param consumer_key: App consumer key.
        :param consumer_secret: App consumer secret.
        :param proxies: Proxies for request.
        :param max_retries: Request max retry times.
        :param timeout: Timeout for request.
        :param chunk_size: Chunk size for read data.
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.proxies = proxies
        self.max_retries = max_retries
        self.timeout = timeout
        self.chunk_size = chunk_size

        self.session = requests.Session()
        self._auth = None
        self.running = False

        if bearer_token:
            self._auth = OAuth2Auth(
                token={"access_token": bearer_token, "token_type": "Bearer"}
            )
        elif all([self.consumer_key, self.consumer_secret]):
            resp = self.generate_bearer_token(
                consumer_key=consumer_key, consumer_secret=consumer_secret
            )
            self._auth = OAuth2Auth(
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
        # make sure only one running connect
        self.running = True
        retries, retry_interval, retry_wait = 1, 2, 2

        try:
            while self.running and retries <= self.max_retries:
                with self.session.get(
                    url=url,
                    params=params,
                    auth=self._auth,
                    proxies=self.proxies,
                    timeout=self.timeout,
                    stream=True,
                ) as resp:
                    logger.debug(resp.headers)
                    if resp.status_code == 200:
                        for line in resp.iter_lines(chunk_size=self.chunk_size):
                            if line:
                                self.on_data(raw_data=line, return_json=return_json)
                            else:
                                self.on_keep_alive()
                            if not self.running:
                                break

                        if resp.raw.closed:
                            self.on_closed(resp)
                    else:
                        self.on_request_error(resp)
                        logger.debug(
                            f"Request connection failed. "
                            f"Trying again in {retry_wait} seconds... ({retries}/{self.max_retries})"
                        )
                        time.sleep(retry_wait)

                        retries += 1
                        retry_wait = retry_interval * retries
        except Exception as exc:
            logger.exception(f"Exception in request, exc: {exc}")
        finally:
            logger.debug("Request connection exited")
            self.session.close()
            self.disconnect()

    def disconnect(self):
        self.running = False

    def on_data(self, raw_data, return_json=False):
        """
        :param raw_data: Response data by twitter api.
        :param return_json:
        :return:
        """
        data = json.loads(raw_data)
        if not return_json:
            data = data.get("data")
            data = md.Tweet.new_from_json_dict(data=data)

        return self.on_tweet(tweet=data)

    def on_tweet(self, tweet):
        """
        :param tweet: Tweet obj or json data.
        :return:
        """
        logger.debug(f"Received tweet: {tweet}")

    def on_keep_alive(self):
        """
        Refer: https://developer.twitter.com/en/docs/twitter-api/tweets/sampled-stream/integrate/handling-disconnections
        :return:
        """
        logger.debug("Received keep alive signal")

    def on_request_error(self, resp):
        logger.debug(f"Received error status code: {resp.status_code}")

    def on_closed(self, resp):
        logger.debug("Received closed response")

    def sample_stream(
        self,
        *,
        backfill_minutes: Optional[int] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Streams about 1% of all Tweets in real-time.

        :param backfill_minutes: Minutes for disconnection with reconnected stream.
            Accepted value is 1 to 5.
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object.
        :param media_fields: Fields for the media object.
        :param place_fields: Fields for the place object.
        :param poll_fields: Fields for the poll object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        """

        if self.running:
            raise PyTwitterError("Stream is running")

        args = {
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "place.fields": enf_comma_separated(
                name="place_fields", value=place_fields
            ),
            "poll.fields": enf_comma_separated(name="poll_fields", value=poll_fields),
        }
        if backfill_minutes is not None:
            args["backfill_minutes"] = backfill_minutes

        # connect the stream
        self._connect(
            url=f"{self.BASE_URL}/tweets/sample/stream",
            params=args,
            return_json=return_json,
        )

    def search_stream(
        self,
        *,
        backfill_minutes: Optional[int] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):

        """
        Streams Tweets in real-time based on a specific set of filter rules.

        :param backfill_minutes: Minutes for disconnection with reconnected stream.
            Accepted value is 1 to 5.
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object.
        :param media_fields: Fields for the media object.
        :param place_fields: Fields for the place object.
        :param poll_fields: Fields for the poll object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        """

        if self.running:
            raise PyTwitterError("Stream is running")

        args = {
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "place.fields": enf_comma_separated(
                name="place_fields", value=place_fields
            ),
            "poll.fields": enf_comma_separated(name="poll_fields", value=poll_fields),
        }
        if backfill_minutes is not None:
            args["backfill_minutes"] = backfill_minutes

        # connect the stream
        self._connect(
            url=f"{self.BASE_URL}/tweets/search/stream",
            params=args,
            return_json=return_json,
        )

    def _request(self, url, verb="GET", params=None, json_data=None):
        """
        :param url: Url for twitter api
        :param verb: HTTP Method, like GET,POST.
        :param params: The url params to send in the body of the request.
        :param json_data: The json data to send in the body of the request.
        :return: A json object
        """

        resp = self.session.request(
            url=url,
            method=verb,
            params=params,
            auth=self._auth,
            json=json_data,
            timeout=self.timeout,
            proxies=self.proxies,
        )

        return resp

    @staticmethod
    def _parse_response(resp: Response) -> dict:
        """
        :param resp: Response
        :return: json data
        """
        try:
            data = resp.json()
        except ValueError:
            raise PyTwitterError(f"Unknown error: {resp.content}")

        if not resp.ok:
            raise PyTwitterError(data)

        return data

    def get_rules(
        self, ids: Optional[Union[str, List, Tuple]] = None, return_json=False
    ):
        """
        Return a list of rules currently active on the streaming endpoint, either as a list or individually.

        :param ids: IDs for rule. If omitted, all rules are returned.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response object or json data
        """

        args = {"ids": enf_comma_separated(name="ids", value=ids)}

        resp = self._request(
            url=f"{self.BASE_URL}/tweets/search/stream/rules",
            params=args,
        )
        resp_json = self._parse_response(resp=resp)

        if return_json:
            return resp_json
        else:
            return md.Response(
                data=[
                    md.StreamRule.new_from_json_dict(item)
                    for item in resp_json.get("data", [])
                ],
                meta=md.Meta.new_from_json_dict(resp_json.get("meta")),
            )

    def manage_rules(
        self, rules: Optional[Dict[str, List]], dry_run=False, return_json=False
    ):
        """
        Add or delete rules to your stream.

        :param rules: Json body for your rules.
            See more detail: https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/api-reference/post-tweets-search-stream-rules
        :param dry_run: Set to true can test the syntax of your rules without submitting it.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response object or json data
        """

        resp = self._request(
            url=f"{self.BASE_URL}/tweets/search/stream/rules",
            verb="POST",
            params={"dry_run": dry_run},
            json_data=rules,
        )

        resp_json = self._parse_response(resp=resp)

        if return_json:
            return resp_json
        else:
            errors = resp_json.get("errors")
            return md.Response(
                data=[
                    md.StreamRule.new_from_json_dict(item)
                    for item in resp_json.get("data", [])
                ],
                meta=md.Meta.new_from_json_dict(resp_json.get("meta")),
                errors=[md.Error.new_from_json_dict(err) for err in errors]
                if errors
                else None,
            )
