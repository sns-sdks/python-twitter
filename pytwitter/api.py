"""
    Api Impl
"""
from typing import List, Optional, Tuple, Union

import requests
from requests.models import Response
from requests_oauthlib import OAuth2

import pytwitter.models as md
from pytwitter.error import PyTwitterError
from pytwitter.utils.validators import enf_comma_separated


class Api:
    BASE_URL_V2 = "https://api.twitter.com/2"

    def __init__(
        self,
        bearer_token=None,
        consumer_key=None,
        consumer_secret=None,
        access_token=None,
        access_secret=None,
        application_only_auth=False,
        oauth_flow=False,  # provide access with authorize
        timeout=None,
        proxies=None,
    ):
        self.session = requests.Session()
        self._auth = None
        self.timeout = timeout
        self.proxies = proxies

        # just use bearer token
        if bearer_token:
            self._auth = OAuth2(
                token={"access_token": bearer_token, "token_type": "Bearer"}
            )
        # use app auth
        elif consumer_key and consumer_secret and application_only_auth:
            pass
        # use user auth
        elif all([consumer_key, consumer_secret, access_token, access_secret]):
            pass
        # use oauth flow by hand
        elif consumer_key and consumer_secret and oauth_flow:
            pass
        else:
            raise Exception("Need oauth")

    def set_credentials(self):
        pass

    def _request(self, url, verb="GET", params=None, data=None, enforce_auth=True):
        """
        Request for twitter api url
        :param url: The api location for twitter
        :param verb: HTTP Method, either GET or POST
        :param params: The url params for GET
        :param data: The query data for POST
        :param enforce_auth: Whether need auth
        :return: A json object
        """
        auth = None
        if enforce_auth:
            if not self._auth:
                raise Exception("The twitter.Api instance must be authenticated.")

            auth = self._auth

        resp = self.session.request(
            url=url,
            method=verb,
            params=params,
            data=data,
            auth=auth,
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

        if resp.status_code != 200:
            raise PyTwitterError(data)

        if "errors" in data:
            raise PyTwitterError(data["errors"])

        # v1 token not
        if "reason" in data:
            raise PyTwitterError(data)

        return data

    def _get(self, url, params, cls, multi=False, return_json: bool = False):
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

        data, includes = resp_json["data"], resp_json.get("includes")
        if return_json:
            return data, includes
        else:
            if multi:
                data = [cls.new_from_json_dict(data)]
            else:
                data = cls.new_from_json_dict(data)
            return data, md.Includes.new_from_json_dict(includes)

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

    def get_following(
        self,
        user_id: Optional[str] = None,
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

    def get_followers(
        self,
        user_id: Optional[str] = None,
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
