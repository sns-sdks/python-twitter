"""
    Api Impl
"""
import base64
import logging
import time
from typing import List, Optional, Tuple, Union

import requests
from requests.models import Response
from requests_oauthlib import OAuth1, OAuth2, OAuth1Session

import pytwitter.models as md
from pytwitter.error import PyTwitterError
from pytwitter.rate_limit import RateLimit
from pytwitter.utils.validators import enf_comma_separated

logger = logging.getLogger(__name__)


class Api:
    BASE_URL_V2 = "https://api.twitter.com/2"
    BASE_REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
    BASE_AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize"
    BASE_ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
    DEFAULT_CALLBACK_URI = "https://localhost/"

    def __init__(
        self,
        bearer_token=None,
        consumer_key=None,
        consumer_secret=None,
        access_token=None,
        access_secret=None,
        application_only_auth=False,
        oauth_flow=False,  # provide access with authorize
        sleep_on_rate_limit=False,
        timeout=None,
        proxies=None,
    ):
        self.session = requests.Session()
        self._auth = None
        self._oauth_session = None
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.timeout = timeout
        self.proxies = proxies
        self.rate_limit = RateLimit()
        self.sleep_on_rate_limit = sleep_on_rate_limit

        # just use bearer token
        if bearer_token:
            self._auth = OAuth2(
                token={"access_token": bearer_token, "token_type": "Bearer"}
            )
        # use app auth
        elif consumer_key and consumer_secret and application_only_auth:
            resp = self.generate_bearer_token(
                consumer_key=consumer_key, consumer_secret=consumer_secret
            )
            self._auth = OAuth2(
                token={"access_token": resp["access_token"], "token_type": "Bearer"}
            )
        # use user auth
        elif all([consumer_key, consumer_secret, access_token, access_secret]):
            self._auth = OAuth1(
                client_key=consumer_key,
                client_secret=consumer_secret,
                resource_owner_key=access_token,
                resource_owner_secret=access_secret,
            )
            self.rate_limit = RateLimit("user")
        # use oauth flow by hand
        elif consumer_key and consumer_secret and oauth_flow:
            pass
        else:
            raise PyTwitterError("Need oauth")

    def _request(
        self, url, verb="GET", params=None, data=None, json=None, enforce_auth=True
    ):
        """
        Request for twitter api url
        :param url: The api location for twitter
        :param verb: HTTP Method, like GET,POST,PUT.
        :param params: The url params to send in the body of the request.
        :param data: The form data to send in the body of the request.
        :param json: The json data to send in the body of the request.
        :param enforce_auth: Whether need auth
        :return: A json object
        """
        auth = None
        if enforce_auth:
            if not self._auth:
                raise PyTwitterError("The twitter.Api instance must be authenticated.")

            auth = self._auth

            if url and self.sleep_on_rate_limit:
                limit = self.rate_limit.get_limit(url=url)
                if limit.remaining == 0:
                    s_time = max((limit.reset - time.time()), 0) + 10.0
                    logger.debug(
                        f"Rate limited requesting [{url}], sleeping for [{s_time}]"
                    )
                    time.sleep(s_time)

        resp = self.session.request(
            url=url,
            method=verb,
            params=params,
            data=data,
            auth=auth,
            json=json,
            timeout=self.timeout,
            proxies=self.proxies,
        )

        if url and self.rate_limit:
            self.rate_limit.set_limit(url=url, headers=resp.headers)

        return resp

    def get_authorize_url(self, callback_uri=None, **kwargs):
        """
        Get url which to do authorize.
        :param callback_uri: The URL you wish your user to be redirected to.
        :param kwargs: Optional parameter, like force_login,screen_name and so on.
        :return: link to authorize
        """
        if callback_uri is None:
            callback_uri = self.DEFAULT_CALLBACK_URI
        self._oauth_session = OAuth1Session(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            callback_uri=callback_uri,
        )
        self._oauth_session.fetch_request_token(
            self.BASE_REQUEST_TOKEN_URL, proxies=self.proxies
        )
        return self._oauth_session.authorization_url(self.BASE_AUTHORIZE_URL, **kwargs)

    def generate_access_token(self, response):
        """
        :param response:
        :return:
        """
        if not self._oauth_session:
            raise PyTwitterError("Need get_authorize_url first")

        self._oauth_session.parse_authorization_response(response)

        data = self._oauth_session.fetch_access_token(
            self.BASE_ACCESS_TOKEN_URL, proxies=self.proxies
        )
        self._auth = OAuth1(
            client_key=self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=data["oauth_token"],
            resource_owner_secret=data["oauth_token_secret"],
        )
        return data

    def invalidate_access_token(self) -> dict:
        """
        Revoke an issued OAuth access_token by presenting its client credentials

        :return:
        """
        if not self._auth:
            raise PyTwitterError("Must have authorized credentials")

        if not isinstance(self._auth, OAuth1):
            raise PyTwitterError("Can only revoke oauth1 token")

        resp = requests.post(
            url="https://api.twitter.com/1.1/oauth/invalidate_token",
        )
        data = self._parse_response(resp=resp)
        return data

    def generate_bearer_token(self, consumer_key: str, consumer_secret: str) -> dict:
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
        data = self._parse_response(resp=resp)
        return data

    def invalidate_bearer_token(
        self, consumer_key: str, consumer_secret: str, access_token: str
    ) -> dict:
        """
        Invalidating a Bearer Token

        :param consumer_key: Your app consumer key
        :param consumer_secret: Your app consumer secret
        :param access_token: Token to be invalidated
        :return: token data
        """
        bearer_token = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode())
        headers = {
            "Authorization": f"Basic {bearer_token.decode()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        resp = requests.post(
            url="https://api.twitter.com/oauth2/invalidate_token",
            data={"access_token": access_token},
            headers=headers,
        )
        data = self._parse_response(resp=resp)
        return data

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

        if resp.status_code != 200:
            raise PyTwitterError(data)

        # note:
        # If only errors will raise
        if "errors" in data and len(data.keys()) == 1:
            raise PyTwitterError(data["errors"])

        # v1 token not
        if "reason" in data:
            raise PyTwitterError(data)

        return data

    def _get(
        self,
        url: str,
        params: dict,
        cls,
        multi: bool = False,
        return_json: bool = False,
    ):
        """
        :param url: Url for twitter api
        :param params: Parameters for api
        :param cls: Class for the entity
        :param multi: Whether multiple result
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the entity like user,tweet...
            - includes: If have expansions, will return
        """
        resp = self._request(url=url, params=params)
        resp_json = self._parse_response(resp)

        if return_json:
            return resp_json
        else:
            data, includes, meta, errors = (
                resp_json["data"],
                resp_json.get("includes"),
                resp_json.get("meta"),
                resp_json.get("errors"),
            )
            if multi:
                data = [cls.new_from_json_dict(item) for item in data]
            else:
                data = cls.new_from_json_dict(data)

            res = md.Response(
                data=data,
                includes=md.Includes.new_from_json_dict(includes),
                meta=md.Meta.new_from_json_dict(meta),
                errors=[md.Error.new_from_json_dict(err) for err in errors]
                if errors is not None
                else None,
            )
            return res

    def get_users(
        self,
        *,
        ids: Optional[Union[str, List, Tuple]] = None,
        usernames: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns a variety of information about one or more users specified by the requested IDs or usernames.

        :param ids: The IDs for target users, Up to 100 are allowed in a single request.
        :param usernames: The username for target users, Up to 100 are allowed in a single request.
            Either ids or username is required for this method.
        :param user_fields: Fields for the user object.
        :param expansions: Fields for expansions.
        :param tweet_fields: Fields for the tweet object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the users
            - includes: expansions data.
        """
        args = {
            "ids": enf_comma_separated(name="ids", value=ids),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
        }

        if ids:
            args["ids"] = enf_comma_separated(name="ids", value=ids)
            path = "users"
        elif usernames:
            args["usernames"] = enf_comma_separated(name="usernames", value=usernames)
            path = "users/by"
        else:
            raise PyTwitterError("Specify at least one of ids or usernames")

        return self._get(
            url=f"{self.BASE_URL_V2}/{path}",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def get_user(
        self,
        *,
        user_id: Optional[str] = None,
        username: Optional[str] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns a variety of information about a single user specified by the requested ID or username.

        :param user_id: The ID of target user.
        :param username: The username of target user.
        :param user_fields: Fields for the user object.
        :param expansions: Fields for expansions.
        :param tweet_fields: Fields for the tweet object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the user
            - includes: expansions data.
        """

        args = {
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
        }

        if user_id:
            path = f"users/{user_id}"
        elif username:
            path = f"users/by/username/{username}"
        else:
            raise PyTwitterError("Specify at least one of user_id or username")

        return self._get(
            url=f"{self.BASE_URL_V2}/{path}",
            params=args,
            cls=md.User,
            return_json=return_json,
        )

    def get_tweets(
        self,
        tweet_ids: Optional[Union[str, List, Tuple]],
        *,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns a variety of information about the Tweet specified by the requested ID or list of IDs.

        :param tweet_ids: The IDs for target users, Up to 100 are allowed in a single request.
        :param expansions: Fields for the expansions.
        :param tweet_fields: Fields for the tweet object.
        :param media_fields: Fields for the media object.
        :param place_fields: Fields for the place object.
        :param poll_fields: Fields for the poll object.
        :param user_fields: Fields for the user object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the tweets
            - includes: expansions data.
        """

        args = {
            "ids": enf_comma_separated(name="tweet_ids", value=tweet_ids),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "place.fields": enf_comma_separated(
                name="place_fields", value=place_fields
            ),
            "poll.fields": enf_comma_separated(name="poll_fields", value=poll_fields),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/tweets",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def get_tweet(
        self,
        tweet_id: str,
        *,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns a variety of information about a single Tweet specified by the requested ID.

        :param tweet_id: The ID of target tweet.
        :param expansions: Fields for the expansions.
        :param tweet_fields: Fields for the tweet object.
        :param media_fields: Fields for the media object.
        :param place_fields: Fields for the place object.
        :param poll_fields: Fields for the poll object.
        :param user_fields: Fields for the user object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns:
            - data: data for the tweet self.
            - includes: expansions data.
        """

        args = {
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "place.fields": enf_comma_separated(
                name="place_fields", value=place_fields
            ),
            "poll.fields": enf_comma_separated(name="poll_fields", value=poll_fields),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/tweets/{tweet_id}",
            params=args,
            cls=md.Tweet,
            return_json=return_json,
        )

    def get_following(
        self,
        user_id: str,
        *,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ):
        """
        Returns a list of users the specified user ID is following.

        :param user_id: The user ID whose following you would like to retrieve.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object.
        :param tweet_fields: Fields for the tweet object.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 1000.
        By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the following.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/following",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def follow_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows a user ID to follow another user.
        If the target user does not have public Tweets, this endpoint will send a follow request.

        :param user_id: The user ID who you would like to initiate the follow on behalf of.
                        It must match the username of the authenticating user.
        :param target_user_id: The target user ID of user to follow
        :return: follow status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/following",
            verb="POST",
            json={"target_user_id": target_user_id},
        )
        data = self._parse_response(resp)
        return data

    def unfollow_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows a user ID to unfollow another user.

        :param user_id: The user ID who you would like to initiate the unfollow on behalf of.
                        It must match the username of the authenticating user.
        :param target_user_id: The user ID of user to unfollow.
        :return: follow status data
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/following/{target_user_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp)
        return data

    def get_followers(
        self,
        user_id: str,
        *,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ):
        """
        Returns a list of users who are followers of the specified user ID.

        :param user_id: The user ID whose following you would like to retrieve.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object.
        :param tweet_fields: Fields for the tweet object.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 1000.
        By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the following.
            - includes: expansions data.
            - meta: pagination details
        """
        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/followers",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def get_timelines(
        self,
        user_id: str,
        *,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        exclude: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns Tweets composed by a single user

        :param user_id: The id for target user.
        :param start_time: Oldest or earliest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param end_time: Newest or most recent UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param since_id: Greater than (that is, more recent than) tweet id for response. Exclude this since_id.
        :param until_id: Less than (that is, older than) tweet id for response. Exclude this until_id.
        :param max_results: The maximum number of results to be returned per page. Number between 5 and the 100.
        By default, each page will return 10 results.
        :param pagination_token: Token for the pagination.
        :param tweet_fields: Fields for the tweet object.
        :param exclude: Fields for types of Tweets to exclude from the response.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """

        args = {
            "start_time": start_time,
            "end_time": end_time,
            "since_id": since_id,
            "until_id": until_id,
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "exclude": enf_comma_separated(name="exclude", value=exclude),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "place.fields": enf_comma_separated(
                name="place_fields", value=place_fields
            ),
            "poll.fields": enf_comma_separated(name="poll_fields", value=poll_fields),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/tweets",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def get_mentions(
        self,
        user_id: str,
        *,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns Tweets mentioning user specified by ID.

        :param user_id: The id for target user.
        :param start_time: Oldest or earliest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param end_time: Newest or most recent UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param since_id: Greater than (that is, more recent than) tweet id for response. Exclude this since_id.
        :param until_id: Less than (that is, older than) tweet id for response. Exclude this until_id.
        :param max_results: The maximum number of results to be returned per page. Number between 5 and the 100.
        By default, each page will return 10 results.
        :param pagination_token: Token for the pagination.
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """
        args = {
            "start_time": start_time,
            "end_time": end_time,
            "since_id": since_id,
            "until_id": until_id,
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
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/mentions",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def search_tweets(
        self,
        query: str,
        query_type: str = "recent",
        *,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        max_results: Optional[int] = None,
        next_token: Optional[str] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Search tweets endpoint has two type:
            - recent (default): Returns Tweets from the last seven days that match a search query.
            - all: Returns the complete history of public Tweets matching a search query;
            since the first Tweet was created March 26, 2006.
            But this type only for who have been approved for the `Academic Research product track`.

        :param query: One rule for matching Tweets.
        :param query_type: Accepted values: recent or all
        :param start_time: Oldest or earliest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param end_time: Newest or most recent UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param since_id: Greater than (that is, more recent than) tweet id for response. Exclude this since_id.
        :param until_id: Less than (that is, older than) tweet id for response. Exclude this until_id.
        :param max_results: The maximum number of results to be returned per page. Number between 10 and up to 500.
        By default, each page will return 10 results.
        :param next_token: Token for the pagination.
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """

        args = {
            "query": query,
            "start_time": start_time,
            "end_time": end_time,
            "since_id": since_id,
            "until_id": until_id,
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
            "max_results": max_results,
            "next_token": next_token,
        }

        if query_type == "recent":
            url = f"{self.BASE_URL_V2}/tweets/search/recent"
        elif query_type == "all":
            url = f"{self.BASE_URL_V2}/tweets/search/all"
        else:
            raise PyTwitterError(f"Not support for query type: {query_type}")

        return self._get(
            url=url,
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def hidden_reply(self, tweet_id: str, hidden: Optional[bool] = True) -> dict:
        """
        Hide or un-hide a reply to a Tweet.

        Note: This api must with OAuth 1.0a User context.

        :param tweet_id: ID of the tweet to hide or un-hide,
        :param hidden: If set True, will hide reply, If set False, will un-hide reply. Default is True.
        :return: status for hide or un-hide.
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/tweets/{tweet_id}/hidden",
            verb="PUT",
            json={"hidden": hidden},
        )
        data = self._parse_response(resp=resp)
        return data
