"""
    Api Impl
"""
import base64
import logging
import os
import re
import time
from typing import List, Optional, Tuple, Union

import requests
from requests.models import Response
from authlib.integrations.requests_client import (
    OAuth2Session,
    OAuth2Auth,
    OAuth1Auth,
    OAuth1Session,
)

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
    BASE_OAUTH2_AUTHORIZE_URL = "https://twitter.com/i/oauth2/authorize"
    BASE_OAUTH2_ACCESS_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
    DEFAULT_SCOPES = ["users.read", "tweet.read"]

    def __init__(
        self,
        bearer_token: Optional[str] = None,
        consumer_key: Optional[str] = None,
        consumer_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_secret: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        application_only_auth: bool = False,
        oauth_flow: bool = False,  # provide access with authorize
        sleep_on_rate_limit: bool = False,
        timeout: Optional[int] = None,
        proxies: Optional[dict] = None,
        callback_uri: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ) -> None:
        """
        Initial the Api instance.

        :param bearer_token: OAuth2.0 Token for app.
        :param consumer_key: Consumer key for app.
        :param consumer_secret: Consumer secret for app.
        :param access_token: Access token for the authenticated user.
        :param access_secret: Access token secret for the authenticated user.
        :param client_id: Client ID for app with OAuth2.0
        :param client_secret: Client Secret for app with OAuth2.0.
            When your app are confidential clients, You need provide this.
        :param application_only_auth: If set this, with auto exchange app bearer token with consumer credentials.
        :param oauth_flow: If set this, You need generate access token with user by OAuth1.1 or OAuth2.0
        :param sleep_on_rate_limit: If token reach the limit, will sleep.
        :param timeout: Timeout for requests.
        :param proxies: Proxies for requests.
        :param callback_uri: Your callback URL. This value must correspond to one of the Callback URLs defined in your App settings.
        :param scopes: Scopes allow you to set granular access for your App so that your App only has the permissions that it needs.
        """
        self.session = requests.Session()
        self._auth = None
        self._oauth_session = None
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.proxies = proxies
        self.rate_limit = RateLimit()
        self.sleep_on_rate_limit = sleep_on_rate_limit
        self.auth_user_id = None  # Note: use this keep uid for auth user
        self.callback_uri = (
            callback_uri if callback_uri is not None else self.DEFAULT_CALLBACK_URI
        )
        self.scopes = scopes if scopes is not None else self.DEFAULT_SCOPES

        # just use bearer token
        if bearer_token:
            self._auth = OAuth2Auth(
                token={"access_token": bearer_token, "token_type": "Bearer"}
            )
        # use app auth
        elif consumer_key and consumer_secret and application_only_auth:
            resp = self.generate_bearer_token(
                consumer_key=consumer_key, consumer_secret=consumer_secret
            )
            self._auth = OAuth2Auth(
                token={"access_token": resp["access_token"], "token_type": "Bearer"}
            )
        # use user auth
        elif all([consumer_key, consumer_secret, access_token, access_secret]):
            self._auth = OAuth1Auth(
                client_id=consumer_key,
                client_secret=consumer_secret,
                token=access_token,
                token_secret=access_secret,
            )
            self.rate_limit = RateLimit("user")
            self.auth_user_id = self.get_uid_from_access_token_key(
                access_token=access_token
            )
        # use oauth flow by hand
        elif consumer_key and consumer_secret and oauth_flow:
            pass
        elif client_id and oauth_flow:
            pass
        else:
            raise PyTwitterError("Need oauth")

    @staticmethod
    def get_uid_from_access_token_key(access_token: str) -> str:
        """
        Get uid from access token, ex: 1323843269210460160-xxx
        :param access_token: Access token
        :return: uid
        """
        uid, _ = access_token.split("-")
        return uid

    def _request(
        self, url, verb="GET", params=None, data=None, json=None, enforce_auth=True
    ) -> Response:
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
                limit = self.rate_limit.get_limit(url=url, method=verb)
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
            self.rate_limit.set_limit(url=url, headers=resp.headers, method=verb)

        return resp

    def _get_oauth1_session(
        self,
        callback_uri: Optional[str] = None,
        **kwargs,
    ) -> OAuth1Session:
        """
        :param callback_uri: The URL that twitter redirect back to after the user logged in.
        :param kwargs: Additional parameters for oauth1.
        :return: OAuth Session
        """
        # check app credentials
        if not (self.consumer_key and self.consumer_secret):
            raise PyTwitterError({"message": "OAuth need your app credentials"})

        if callback_uri is None:
            callback_uri = self.callback_uri

        session = OAuth1Session(
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
            callback_uri=callback_uri,
            **kwargs,
        )
        return session

    def get_authorize_url(self, callback_uri=None, **kwargs) -> str:
        """
        Get url which to do authorize.
        :param callback_uri: The URL you wish your user to be redirected to.
        :param kwargs: Additional parameters for oauth1, like force_login,screen_name and so on.
        :return: link to authorize
        """
        session = self._get_oauth1_session(callback_uri=callback_uri, **kwargs)
        session.fetch_request_token(self.BASE_REQUEST_TOKEN_URL, proxies=self.proxies)
        return session.create_authorization_url(self.BASE_AUTHORIZE_URL, **kwargs)

    def generate_access_token(
        self, response: str, callback_uri: str = None, **kwargs
    ) -> dict:
        """
        :param response: Response url after user logged in.
        :param callback_uri: The URL you wish your user to be redirected to.
        :param kwargs: Additional parameters for oauth1.
        :return:
        """
        session = self._get_oauth1_session(callback_uri=callback_uri, **kwargs)
        session.parse_authorization_response(response)

        data = session.fetch_access_token(
            self.BASE_ACCESS_TOKEN_URL, proxies=self.proxies
        )
        self._auth = OAuth1Auth(
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
            token=data["oauth_token"],
            token_secret=data["oauth_token_secret"],
        )
        if "user_id" in data:
            self.auth_user_id = data["user_id"]
        else:
            self.auth_user_id = self.get_uid_from_access_token_key(
                access_token=data["oauth_token"]
            )
        return data

    def invalidate_access_token(self) -> dict:
        """
        Revoke an issued OAuth access_token by presenting its client credentials

        :return:
        """
        if not self._auth:
            raise PyTwitterError("Must have authorized credentials")

        if not isinstance(self._auth, OAuth1Auth):
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

    def _get_oauth2_session(
        self,
        redirect_uri: Optional[str] = None,
        scope: Optional[List[str]] = None,
        **kwargs,
    ) -> OAuth2Session:
        """
        :param redirect_uri: The URL that twitter redirect back to after the user logged in.
        :param scope: A list of permission string to request from the user to using your app.
        :param kwargs: Additional parameters for oauth.
        :return: OAuth Session
        """
        # check app credentials
        if not self.client_id:
            raise PyTwitterError({"message": "OAuth need your app credentials"})

        if redirect_uri is None:
            redirect_uri = self.callback_uri
        if scope is None:
            scope = self.scopes

        session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=scope,
            redirect_uri=redirect_uri,
            code_challenge_method="S256",
            **kwargs,
        )
        return session

    def get_oauth2_authorize_url(
        self, redirect_uri: str = None, scope: Optional[List[str]] = None, **kwargs
    ) -> Tuple[str, str, str]:
        """
        :param redirect_uri: The URL that twitter redirect back to after the user logged in.
        :param scope: A list of permission string to request from the user to using your app.
        :param kwargs: Additional parameters for oauth.
        :return: Authorization url, code_verifier, state
        """
        session = self._get_oauth2_session(
            redirect_uri=redirect_uri,
            scope=scope,
            **kwargs,
        )
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

        authorization_url, state = session.create_authorization_url(
            url=self.BASE_OAUTH2_AUTHORIZE_URL, code_verifier=code_verifier
        )
        return authorization_url, code_verifier, state

    def generate_oauth2_access_token(
        self, response: str, code_verifier: str, redirect_uri: str = None
    ) -> dict:
        """
        :param response: Response url after user logged in.
        :param code_verifier: Code verifier when your
        :param redirect_uri:
        :return:
        """
        session = self._get_oauth2_session(redirect_uri=redirect_uri)

        token = session.fetch_token(
            url=self.BASE_OAUTH2_ACCESS_TOKEN_URL,
            authorization_response=response,
            code_verifier=code_verifier,
            proxies=self.proxies,
        )
        self._auth = OAuth2Auth(token=token)
        return token

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
        params: Optional[dict],
        cls,
        multi: bool = False,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
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
                resp_json.get("data", []),
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
    ) -> Union[dict, md.Response]:
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
    ) -> Union[dict, md.Response]:
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

    def create_tweet(
        self,
        *,
        text: Optional[str] = None,
        direct_message_deep_link: Optional[str] = None,
        for_super_followers_only: Optional[bool] = None,
        geo_place_id: Optional[str] = None,
        media_media_ids: Optional[List[str]] = None,
        media_tagged_user_ids: Optional[List[str]] = None,
        poll_duration_minutes: Optional[int] = None,
        poll_options: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        reply_exclude_reply_user_ids: Optional[List[str]] = None,
        reply_in_reply_to_tweet_id: Optional[str] = None,
        reply_settings: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Tweet]:
        """
        Creates a Tweet on behalf of an authenticated user.

        :param text: Text of the Tweet being created. This field is required if media.media_ids is not present.
        :param direct_message_deep_link: Tweets a link directly to a Direct Message conversation with an account.
        :param for_super_followers_only: Allows you to Tweet exclusively for Super Followers.
        :param geo_place_id: Place ID being attached to the Tweet for geo location.
        :param media_media_ids: A list of Media IDs being attached to the Tweet.
            This is only required if the request includes the tagged_user_ids.
        :param media_tagged_user_ids: A list of User IDs being tagged in the Tweet with Media.
            If the user you're tagging doesn't have photo-tagging enabled, their names won't show up
            in the list of tagged users even though the Tweet is successfully created.
        :param poll_duration_minutes: Duration of the poll in minutes for a Tweet with a poll.
            This is only required if the request includes poll.options
        :param poll_options: A list of poll options for a Tweet with a poll.
            For the request to be successful it must also include duration_minutes too.
        :param quote_tweet_id: Link to the Tweet being quoted.
        :param reply_exclude_reply_user_ids: A list of User IDs to be excluded from the reply Tweet
            thus removing a user from a thread.
        :param reply_in_reply_to_tweet_id: Tweet ID of the Tweet being replied to. Please note that in_reply_to_tweet_id
            needs to be in the request if exclude_reply_user_ids is present.
        :param reply_settings: Settings to indicate who can reply to the Tweet.
            Options include "mentionedUsers" and "following". If the field isn’t specified, it will default to everyone.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :returns: Data for tweet created.
        """
        args = {}
        if geo_place_id is not None:
            args["geo"] = {"place_id": geo_place_id}
        if media_media_ids is not None or media_tagged_user_ids is not None:
            args["media"] = {
                "media_ids": media_media_ids,
                "tagged_user_ids": media_tagged_user_ids,
            }
        if poll_duration_minutes is not None or poll_options is not None:
            args["poll"] = {
                "duration_minutes": poll_duration_minutes,
                "options": poll_options,
            }
        if (
            reply_in_reply_to_tweet_id is not None
            or reply_exclude_reply_user_ids is not None
        ):
            args["reply"] = {
                "exclude_reply_user_ids": reply_exclude_reply_user_ids,
                "in_reply_to_tweet_id": reply_in_reply_to_tweet_id,
            }
        if direct_message_deep_link is not None:
            args["direct_message_deep_link"] = direct_message_deep_link
        if for_super_followers_only is not None:
            args["for_super_followers_only"] = for_super_followers_only
        if quote_tweet_id is not None:
            args["quote_tweet_id"] = quote_tweet_id
        if reply_settings is not None:
            args["reply_settings"] = reply_settings
        if text is not None:
            args["text"] = text

        resp = self._request(
            url=f"{self.BASE_URL_V2}/tweets",
            verb="POST",
            json=args,
        )
        data = self._parse_response(resp=resp)
        if return_json:
            return data
        else:
            return md.Tweet.new_from_json_dict(data=data["data"])

    def delete_tweet(
        self,
        tweet_id: str,
    ) -> dict:
        """
        Allows a user or authenticated user ID to delete a Tweet.

        :param tweet_id: ID for the tweet will be deleted.
        :return: Tweet delete status.
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/tweets/{tweet_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp=resp)
        return data

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
    ) -> Union[dict, md.Response]:
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

    def get_timelines_reverse_chronological(
        self,
        user_id: str,
        *,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        exclude: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Allows you to retrieve a collection of the most recent Tweets and Retweets posted by you and users you follow.
        This endpoint returns up to the last 3200 Tweets.

        :param user_id: Unique identifier of the user that is requesting their chronological home timeline.
        :param start_time: Oldest or earliest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param end_time: Newest or most recent UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param since_id: Greater than (that is, more recent than) tweet id for response. Exclude this since_id.
        :param until_id: Less than (that is, older than) tweet id for response. Exclude this until_id.
        :param max_results: The maximum number of results to be returned per page. Number between 5 and the 100.
        By default, each page will return 10 results.
        :param pagination_token: Token for the pagination.
        :param exclude: Fields for types of Tweets to exclude from the response.
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
            "exclude": enf_comma_separated(name="exclude", value=exclude),
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
            url=f"{self.BASE_URL_V2}/users/{user_id}/timelines/reverse_chronological",
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
    ) -> Union[dict, md.Response]:
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
        sort_order: Optional[str] = None,
        next_token: Optional[str] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
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
        :param sort_order: This parameter is used to specify the order in which you want the Tweets returned.
        By default, a request will return the most recent Tweets first (sorted by recency).
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
            "sort_order": sort_order,
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

    def get_tweets_counts(
        self,
        query: str,
        search_type: str = "recent",
        *,
        granularity: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        next_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Get count of Tweets that match a search query.

        :param query: One rule for matching Tweets.
            - Standard Project can use the basic set of operators and can make queries up to 512 characters long
            - Academic Research Project can use all available operators and can make queries up to 1,024 characters long
        :param search_type: Accepted values:
            - recent: For all apps, Only can get tweets from the last seven days.
            - all: only for Academic Research product track. Since the first Tweet was created March 26, 2006.
        :param granularity: The timeseries count data to be grouped by. Can be day, hour or minute
        :param start_time: The oldest UTC timestamp from which the Tweets will be provided.
        :param end_time: The newest, most recent UTC timestamp to which the Tweets will be provided.
        :param since_id: Returns results with a Tweet ID greater than (for example, more recent than) the specified ID.
        :param until_id: Returns results with a Tweet ID less than (that is, older than) the specified ID.
        :param next_token: This parameter is used to get the next 'page' of results.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: Data for the counts.
            - meta: Meta data for request.
        """

        args = {
            "query": query,
            "granularity": granularity,
            "start_time": start_time,
            "end_time": end_time,
            "since_id": since_id,
            "until_id": until_id,
            "next_token": next_token,
        }

        if search_type == "recent":
            url = f"{self.BASE_URL_V2}/tweets/counts/recent"
        elif search_type == "all":
            url = f"{self.BASE_URL_V2}/tweets/counts/all"
        else:
            raise PyTwitterError(f"Not support type for {search_type}")

        return self._get(
            url=url,
            params=args,
            cls=md.TweetCount,
            multi=True,
            return_json=return_json,
        )

    def get_tweet_quote_tweets(
        self,
        tweet_id: str,
        *,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns Quote Tweets for a Tweet specified by the requested Tweet ID.

        :param tweet_id: Unique identifier of the Tweet to request.
        :param expansions: Fields for the expansions.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 10 and the 1000.
        By default, each page will return 100 results.
        :param tweet_fields: Fields for the tweet object.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
            - meta: pagination details
        """
        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
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
            url=f"{self.BASE_URL_V2}/tweets/{tweet_id}/quote_tweets",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def get_tweet_retweeted_users(
        self,
        tweet_id: str,
        *,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Get information about who has Retweeted a Tweet.

        :param tweet_id: The tweet ID whose retweeted users you would like to retrieve.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
        By default, each page will return 100 results.
        :param user_fields: Fields for the user object.
        :param expansions: Fields for the expansions now only `pinned_tweet_id`.
        :param tweet_fields: Fields for the tweet object, Expansions required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the users.
            - includes: expansions data.
            - meta: pagination details
        """
        args = {
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/tweets/{tweet_id}/retweeted_by",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def retweet_tweet(self, user_id: str, tweet_id: str) -> dict:
        """
        Allows user to retweet a tweet.
        :param user_id: The user ID who you are retweeting a Tweet on behalf of.
                It must match your user ID which authorize with the access token.
        :param tweet_id: The ID of the Tweet that you would retweet.
        :return: retweet status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/retweets",
            verb="POST",
            json={"tweet_id": tweet_id},
        )
        data = self._parse_response(resp=resp)
        return data

    def remove_retweet_tweet(self, user_id: str, tweet_id: str) -> dict:
        """
        Allows a user to remove the Retweet of a Tweet.

        :param user_id: The user ID who you are removing a Retweet of a Tweet on behalf of.
                It must match your user ID which authorize with the access token.
        :param tweet_id: The ID of the Tweet that you would remove retweet status.
        :return: retweet status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/retweets/{tweet_id}", verb="DELETE"
        )
        data = self._parse_response(resp=resp)
        return data

    def get_tweet_liking_users(
        self,
        tweet_id: str,
        *,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Get information about a Tweet’s liking users.

        :param tweet_id: The tweet ID whose liking users you would like to retrieve.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
        By default, each page will return 100 results.
        :param expansions: Fields for the expansions.
        By default, each page will return 100 results.
        :param tweet_fields: Fields for the tweet object.
        :param user_fields: Fields for the user object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the users.
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
            url=f"{self.BASE_URL_V2}/tweets/{tweet_id}/liking_users",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def get_user_liked_tweets(
        self,
        user_id: str,
        *,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Get information about a user’s liked Tweets.

        :param user_id: The user ID whose liked tweets you would like to retrieve.
        :param expansions: Fields for the expansions.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 1000.
        By default, each page will return 100 results.
        :param tweet_fields: Fields for the tweet object.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
            - meta: pagination details
        """
        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
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
            url=f"{self.BASE_URL_V2}/users/{user_id}/liked_tweets",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def like_tweet(self, user_id: str, tweet_id: str) -> dict:
        """
        Allows user to like tweet.

        :param user_id: The user ID who you are liking a Tweet on behalf of.
                It must match your user ID which authorize with the access token.
        :param tweet_id: The ID of the Tweet that you would like.
        :return: like status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/likes",
            verb="POST",
            json={"tweet_id": tweet_id},
        )
        data = self._parse_response(resp=resp)
        return data

    def unlike_tweet(self, user_id: str, tweet_id: str) -> dict:
        """
        Allows user to remove like status from a tweet.

        :param user_id: The user ID who you are removing a Like of a Tweet on behalf of.
                It must match your user ID which authorize with the access token.
        :param tweet_id: The ID of the Tweet that you would remove like status.
        :return: like status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/likes/{tweet_id}", verb="DELETE"
        )
        data = self._parse_response(resp=resp)
        return data

    def get_bookmark_tweets(
        self,
        user_id: str,
        *,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Allows you to get information about an authenticated user’s 800 most recent bookmarked Tweets.

        :param user_id: The user ID whose bookmark tweets you would like to retrieve.
        :param expansions: Fields for the expansions.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 1000.
        By default, each page will return 100 results.
        :param tweet_fields: Fields for the tweet object.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
            - meta: pagination details
        """
        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
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
            url=f"{self.BASE_URL_V2}/users/{user_id}/bookmarks",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def bookmark_tweet(self, user_id, tweet_id: str) -> dict:
        """
        Causes the user ID of an authenticated user identified in the path parameter to Bookmark the target Tweet provided in the request body.

        :param user_id: The user ID who you are liking a Tweet on behalf of.
                It must match your user ID which authorize with the access token.
        :param tweet_id: The ID of the Tweet that you would to bookmark.
        :return: bookmark status data
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/bookmarks",
            verb="POST",
            json={"tweet_id": tweet_id},
        )
        data = self._parse_response(resp=resp)
        return data

    def bookmark_tweet_remove(self, user_id, tweet_id: str) -> dict:
        """
        Allows a user or authenticated user ID to remove a Bookmark of a Tweet.

        :param user_id: The user ID who you are removing a Like of a Tweet on behalf of.
                It must match your user ID which authorize with the access token.
        :param tweet_id: The ID of the Tweet that you would remove bookmark.
        :return: bookmark status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/bookmarks/{tweet_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp=resp)
        return data

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

    def get_users(
        self,
        *,
        ids: Optional[Union[str, List, Tuple]] = None,
        usernames: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
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
    ) -> Union[dict, md.Response]:
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

    def get_me(
        self,
        *,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ):
        """
        Returns information about an authorized user.

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

        return self._get(
            url=f"{self.BASE_URL_V2}/users/me",
            params=args,
            cls=md.User,
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
    ) -> Union[dict, md.Response]:
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
    ) -> Union[dict, md.Response]:
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

    def follow_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows a user ID to follow another user.
        If the target user does not have public Tweets, this endpoint will send a follow request.

        :param user_id: The user ID who you would like to initiate the follow on behalf of.
                        It must match the authenticating user.
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

    def get_blocking_users(
        self,
        user_id: str,
        *,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of users who are blocked by the specified user ID.

        :param user_id: The user ID whose blocking you would like to retrieve.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object.
        :param tweet_fields: Fields for the tweet object.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 1000.
        By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the blocking.
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
            url=f"{self.BASE_URL_V2}/users/{user_id}/blocking",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def block_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows user to block target user.

        :param user_id: The user ID who you would like to initiate the block on behalf of.
                It must match your user ID which authorize with the access token.
        :param target_user_id: The target user ID of user to block
        :return: block status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/blocking",
            verb="POST",
            json={"target_user_id": target_user_id},
        )
        data = self._parse_response(resp)
        return data

    def unblock_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows user to unblock another user.

        :param user_id: The user ID who you would like to initiate an unblock on behalf of.
                It must match your user ID which authorize with the access token.
        :param target_user_id: The target user ID of user to block
        :return: delete block status data
        """

        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/blocking/{target_user_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp)
        return data

    def get_user_muting(
        self,
        user_id: str,
        *,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of users who are muted by the specified user ID.

        :param user_id: ID for user which you want to get muting.
        :param user_fields: Fields for the user object.
        :param expansions: Fields for the expansions now only `pinned_tweet_id`.
        :param tweet_fields: Fields for the tweet object, Expansions required.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 1000.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the users.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/muting",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def mute_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows user to mute the target user.

        :param user_id: The user ID who you would like to initiate the mute on behalf of.
            It must match your own user ID or that of an authenticating user
        :param target_user_id: The user ID of the user that you would like the id to mute.
        :return: Mute status data
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/muting",
            verb="POST",
            json={"target_user_id": target_user_id},
        )
        data = self._parse_response(resp)
        return data

    def unmute_user(self, user_id: str, target_user_id: str) -> dict:
        """
        Allows user to unmute the target user.

        :param user_id: The user ID who you would like to initiate an unmute on behalf of.
            It must match your own user ID or that of an authenticating user
        :param target_user_id: The user ID of the user that you would like to unmute.
        :return: Unmute status data
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/muting/{target_user_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp)
        return data

    def get_space(
        self,
        space_id: str,
        *,
        space_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        topic_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a variety of information about a single Space specified by the requested ID.

        :param space_id: The ID for the target space.
        :param space_fields: Fields for the space object.
        :param expansions: Fields for expansions.
        :param topic_fields: Fields for the topic object.
        :param user_fields: Fields for the user object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the space
            - includes: expansions data.
        """

        args = {
            "space.fields": enf_comma_separated(
                name="space_fields",
                value=space_fields,
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "topic.fields": enf_comma_separated(
                name="topic_fields", value=topic_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/spaces/{space_id}",
            params=args,
            cls=md.Space,
            return_json=return_json,
        )

    def get_spaces(
        self,
        space_ids: Union[str, List, Tuple],
        *,
        space_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        topic_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns details for multiple Spaces. Up to 100 comma-separated Spaces IDs can be looked up using this endpoint.

        :param space_ids: The IDs for target spaces, Up to 100 are allowed in a single request.
        :param space_fields: Fields for the space object.
        :param expansions: Fields for expansions.
        :param topic_fields: Fields for the topic object.
        :param user_fields: Fields for the user object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the spaces
            - includes: expansions data.
        """
        args = {
            "ids": enf_comma_separated(name="space_ids", value=space_ids),
            "space.fields": enf_comma_separated(
                name="space_fields",
                value=space_fields,
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "topic.fields": enf_comma_separated(
                name="topic_fields", value=topic_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/spaces",
            params=args,
            cls=md.Space,
            multi=True,
            return_json=return_json,
        )

    def get_spaces_by_creator(
        self,
        creator_ids: Union[str, List, Tuple],
        *,
        space_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        topic_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns live or scheduled Spaces created by the specified user IDs.
        Up to 100 comma-separated IDs can be looked up using this endpoint.

        :param creator_ids: IDs for the creators, Up to 100 are allowed in a single request.
        :param space_fields: Fields for the space object.
        :param expansions: Fields for expansions.
        :param topic_fields: Fields for the topic object.
        :param user_fields: Fields for the user object.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the spaces
            - includes: expansions data.
        """
        args = {
            "user_ids": enf_comma_separated(name="creator_ids", value=creator_ids),
            "space.fields": enf_comma_separated(
                name="space_fields",
                value=space_fields,
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "topic.fields": enf_comma_separated(
                name="topic_fields", value=topic_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "max_results": max_results,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/spaces/by/creator_ids",
            params=args,
            cls=md.Space,
            multi=True,
            return_json=return_json,
        )

    def get_buyers_by_space(
        self,
        space_id: str,
        *,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of user who purchased a ticket to the requested Space. You must authenticate the request using the Access Token of the creator of the requested Space.

        :param space_id: The space ID whose buyers you would like to retrieve.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object.
        :param tweet_fields: Fields for the tweet object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the blocking.
            - includes: expansions data.
        """
        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/spaces/{space_id}/buyers",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def get_tweets_by_space(
        self,
        space_id: str,
        *,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns Tweets shared in the requested Spaces.

        :param space_id: The ID for space containing the Tweets you'd like to access.
        :param expansions: Fields for the expansions.
        :param tweet_fields: Fields for the tweet object.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
        """
        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "place.fields": enf_comma_separated(
                name="place_fields", value=place_fields
            ),
            "poll.fields": enf_comma_separated(name="poll_fields", value=poll_fields),
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/spaces/{space_id}/tweets",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def search_spaces(
        self,
        query: str,
        *,
        state: Optional[str] = None,
        space_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        topic_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Return live or scheduled Spaces matching your specified search terms

        :param query: Your search term.
            This can be any text (including mentions and Hashtags) present in the title of the Space.
        :param state: Determines the type of results to return.
            Accepted values: live,scheduled
        :param space_fields: Fields for the space object.
        :param expansions: Fields for expansions.
        :param topic_fields: Fields for the topic object.
        :param user_fields: Fields for the user object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the spaces
            - includes: expansions data.
        """

        args = {
            "query": query,
            "state": state,
            "space.fields": enf_comma_separated(
                name="space_fields",
                value=space_fields,
            ),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "topic.fields": enf_comma_separated(
                name="topic_fields", value=topic_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/spaces/search",
            params=args,
            cls=md.Space,
            multi=True,
            return_json=return_json,
        )

    def get_list(
        self,
        list_id: str,
        *,
        list_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns the details of a specified List.

        :param list_id: ID for the list.
        :param list_fields: Fields for the list object.
        :param expansions: Fields for expansions.
        :param user_fields: Fields for the user object.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the list
            - includes: expansions data.
        """

        args = {
            "list.fields": enf_comma_separated(name="list_fields", value=list_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/lists/{list_id}",
            params=args,
            cls=md.TwitterList,
            return_json=return_json,
        )

    def get_user_owned_lists(
        self,
        user_id: str,
        *,
        list_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns all Lists owned by the specified user.

        :param user_id: ID for the user.
        :param list_fields: Fields for the list object.
        :param expansions: Fields for expansions.
        :param user_fields: Fields for the user object. Expansion required.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
            By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data for the lists
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "list.fields": enf_comma_separated(name="list_fields", value=list_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/owned_lists",
            params=args,
            cls=md.TwitterList,
            multi=True,
            return_json=return_json,
        )

    def create_list(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        private: Optional[bool] = None,
        return_json: bool = False,
    ) -> Union[md.TwitterList, dict]:
        """
        Enables the authenticated user to create a List.

        :param name: The name of the List you wish to create.
        :param description: Description of the List.
        :param private: Determine whether the List should be private.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Twitter List information.
        """

        args = {"name": name}
        if description is not None:
            args["description"] = description
        if private is not None:
            args["private"] = private

        resp = self._request(
            url=f"{self.BASE_URL_V2}/lists",
            verb="POST",
            json=args,
        )
        data = self._parse_response(resp=resp)
        if return_json:
            return data
        else:
            return md.TwitterList.new_from_json_dict(data["data"])

    def update_list(
        self,
        list_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        private: Optional[bool] = None,
    ) -> dict:
        """
        Enables the authenticated user to update the meta data of a specified List that they own.

        :param list_id: The ID of the List to be updated.
        :param name: Updates the name of the List.
        :param description: Updates the description of the List.
        :param private: Determines whether the List should be private.
        :return: Status for update twitter list.
        """

        args = {}
        if name is not None:
            args["name"] = name
        if description is not None:
            args["description"] = description
        if private is not None:
            args["private"] = private

        resp = self._request(
            url=f"{self.BASE_URL_V2}/lists/{list_id}",
            verb="PUT",
            json=args,
        )
        data = self._parse_response(resp=resp)
        return data

    def delete_list(self, list_id: str) -> dict:
        """
        Enables the authenticated user to delete a List that they own.

        :param list_id: The ID of the List to be deleted.
        :return: Status for delete list.
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/lists/{list_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp=resp)
        return data

    def get_list_tweets(
        self,
        list_id: str,
        *,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        place_fields: Optional[Union[str, List, Tuple]] = None,
        poll_fields: Optional[Union[str, List, Tuple]] = None,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of Tweets from the specified List.

        :param list_id: ID for the list
        :param tweet_fields: Fields for the tweet object.
        :param expansions: Fields for the expansions.
        :param user_fields: Fields for the user object, Expansion required.
        :param media_fields: Fields for the media object, Expansion required.
        :param place_fields: Fields for the place object, Expansion required.
        :param poll_fields: Fields for the poll object, Expansion required.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
            By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
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
            url=f"{self.BASE_URL_V2}/lists/{list_id}/tweets",
            params=args,
            cls=md.Tweet,
            multi=True,
            return_json=return_json,
        )

    def get_list_members(
        self,
        list_id: str,
        *,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of users who are members of the specified List.

        :param list_id: ID for the list.
        :param user_fields: Fields for the user object.
        :param expansions: Fields for expansions.
        :param tweet_fields: Fields for the tweet object.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
            By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/lists/{list_id}/members",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def get_user_memberships_lists(
        self,
        user_id: str,
        *,
        list_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns all Lists a specified user is a member of.

        :param user_id: ID for the user.
        :param list_fields: Fields for the list object.
        :param expansions: Fields for expansions.
        :param user_fields: Fields for the user object. Expansion required.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
            By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data for the lists.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "list.fields": enf_comma_separated(name="list_fields", value=list_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/list_memberships",
            params=args,
            cls=md.TwitterList,
            multi=True,
            return_json=return_json,
        )

    def add_list_member(
        self,
        *,
        list_id: str,
        user_id: str,
    ) -> dict:
        """
        Enables the authenticated user to add a member to a List they own.

        :param list_id: The ID of the List you are adding a member to.
        :param user_id: The ID of the user you wish to add as a member of the List.
        :return: Member added status
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/lists/{list_id}/members",
            verb="POST",
            json={"user_id": user_id},
        )
        data = self._parse_response(resp=resp)
        return data

    def remove_list_member(
        self,
        *,
        list_id: str,
        user_id: str,
    ) -> dict:
        """
        Enables the authenticated user to remove a member from a List they own.

        :param list_id: The ID of the List you are removing a member from.
        :param user_id: The ID of the user you wish to remove as a member of the List.
        :return: Member remove status
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/lists/{list_id}/members/{user_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp=resp)
        return data

    def follow_list(
        self,
        *,
        user_id: str,
        list_id: str,
    ) -> dict:
        """
        Enables the authenticated user to follow a List.

        :param user_id: The user ID who you are following a List on behalf of, with access token associated.
        :param list_id: The ID of the List that you would like the user id to follow.
        :return: Follow list status
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/followed_lists",
            verb="POST",
            json={"list_id": list_id},
        )
        data = self._parse_response(resp=resp)
        return data

    def unfollow_list(
        self,
        *,
        user_id: str,
        list_id: str,
    ) -> dict:
        """
        Enables the authenticated user to unfollow a List.

        :param user_id: The user ID who you are unfollowing a List on behalf of, with access token associated.
        :param list_id: The ID of the List that you would like the user id to unfollow.
        :return: Unfollow list status.
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/followed_lists/{list_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp=resp)
        return data

    def get_list_followers(
        self,
        list_id: str,
        *,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of users who are followers of the specified List.

        :param list_id: ID for the list.
        :param user_fields: Fields for the user object.
        :param expansions: Fields for expansions.
        :param tweet_fields: Fields for the tweet object.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
            By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the tweets.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/lists/{list_id}/followers",
            params=args,
            cls=md.User,
            multi=True,
            return_json=return_json,
        )

    def get_user_followed_lists(
        self,
        user_id: str,
        *,
        list_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns all Lists a specified user follows.

        :param user_id: ID for the user.
        :param list_fields: Fields for the list object.
        :param expansions: Fields for expansions.
        :param user_fields: Fields for the user object. Expansion required.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and the 100.
            By default, each page will return 100 results.
        :param pagination_token: Token for the pagination.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data for the lists.
            - includes: expansions data.
            - meta: pagination details
        """

        args = {
            "list.fields": enf_comma_separated(name="list_fields", value=list_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }

        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/followed_lists",
            params=args,
            cls=md.TwitterList,
            multi=True,
            return_json=return_json,
        )

    def get_user_pinned_lists(
        self,
        user_id: str,
        *,
        list_fields: Optional[Union[str, List, Tuple]] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns the Lists pinned by a specified user.

        :param user_id: ID for the user.
        :param list_fields: Fields for the list object.
        :param expansions: Fields for expansions.
        :param user_fields: Fields for the user object. Expansion required.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data for the lists
            - includes: expansions data.
            - meta: pagination details
        """
        args = {
            "list.fields": enf_comma_separated(name="list_fields", value=list_fields),
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/users/{user_id}/pinned_lists",
            params=args,
            cls=md.TwitterList,
            multi=True,
            return_json=return_json,
        )

    def pin_list(
        self,
        *,
        user_id: str,
        list_id: str,
    ) -> dict:
        """
        Enables the authenticated user to pin a List.

        :param user_id: The user ID who you are pinning a List on behalf of, with access token associated.
        :param list_id: The ID of the List that you would like the user id to pin.
        :return: Pin list status.
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/pinned_lists",
            verb="POST",
            json={"list_id": list_id},
        )
        data = self._parse_response(resp=resp)
        return data

    def unpin_list(
        self,
        *,
        user_id: str,
        list_id: str,
    ) -> dict:
        """
        Enables the authenticated user to unpin a List.

        :param user_id: The user ID who you are unpin a List on behalf of, with access token associated.
        :param list_id: The ID of the List that you would like the user id to unpin.
        :return: unpin list status.
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/users/{user_id}/pinned_lists/{list_id}",
            verb="DELETE",
        )
        data = self._parse_response(resp=resp)
        return data

    def get_compliance_job(
        self,
        job_id: str,
        *,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Get a single compliance job with the specified ID.

        :param job_id: ID for the compliance job.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the job.
        """

        return self._get(
            url=f"{self.BASE_URL_V2}/compliance/jobs/{job_id}",
            params=None,
            cls=md.ComplianceJob,
            return_json=return_json,
        )

    def get_compliance_jobs(
        self,
        job_type: Optional[str],
        *,
        status: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of recent compliance jobs.

        :param job_type: Type for the job, Accepted values are: tweets, users.
        :param status: Status for the job.
            Accepted values are: created, in_progress, failed, complete.
            Default is all.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return:
            - data: data for the jobs.
        """

        args = {"type": job_type}
        if status:
            args["status"] = status

        return self._get(
            url=f"{self.BASE_URL_V2}/compliance/jobs",
            params=args,
            cls=md.ComplianceJob,
            multi=True,
            return_json=return_json,
        )

    def create_compliance_job(
        self,
        job_type: Optional[str],
        *,
        name: Optional[str] = None,
        resumable: Optional[bool] = None,
        return_json: bool = False,
    ) -> Union[dict, md.ComplianceJob]:
        """
        Creates a new compliance job for Tweet IDs or user IDs.
        You can run one batch job at a time.

        :param job_type: Type for the job, Accepted values are: tweets, users.
        :param name: A name for this job, useful to identify multiple jobs using a label you define.
        :param resumable: Specifies whether to enable the upload URL with support for resumable uploads
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Compliance job information.
        """

        args = {"type": job_type}
        if name is not None:
            args["name"] = name
        if resumable is not None:
            args["resumable"] = resumable

        resp = self._request(
            url=f"{self.BASE_URL_V2}/compliance/jobs",
            verb="POST",
            json=args,
        )
        data = self._parse_response(resp=resp)
        if return_json:
            return data
        else:
            return md.ComplianceJob.new_from_json_dict(data["data"])

    def get_dm_events_by_participant(
        self,
        participant_id: str,
        *,
        dm_event_fields: Optional[Union[str, List, Tuple]] = None,
        event_types: Optional[str] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of Direct Messages (DM) events within a 1-1 conversation with the user
        specified in the participant_id path parameter.

        :param participant_id: The participant_id of the user is having a 1-1 conversation with.
        :param dm_event_fields: Fields for the direct message events.
        :param event_types: Type of Direct Message event to return. In the context of one-to-one conversations,
        only `MessageCreate` is relevant.
        :param expansions: Fields for the expansions.
        :param media_fields: Fields for the media object, Expansion required.
        :param user_fields: Fields for the user object, Expansion required.
        :param tweet_fields: Fields for the tweet object, Expansion required.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and up to 100.
        By default, each page will return 100 results.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """

        args = {
            "dm_event.fields": enf_comma_separated(
                name="dm_event_fields",
                value=dm_event_fields,
            ),
            "event_types": event_types,
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/dm_conversations/with/{participant_id}/dm_events",
            params=args,
            cls=md.DirectMessageEvent,
            multi=True,
            return_json=return_json,
        )

    def get_dm_events_by_conversation(
        self,
        dm_conversation_id: str,
        *,
        dm_event_fields: Optional[Union[str, List, Tuple]] = None,
        event_types: Optional[str] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of Direct Messages within a conversation specified in the `dm_conversation_id` path parameter.

        :param dm_conversation_id: The `id` of the Direct Message conversation for which events are being retrieved.
        :param dm_event_fields: Fields for the direct message events.
        :param event_types: Type of Direct Message event to return. In the context of one-to-one conversations,
        only `MessageCreate` is relevant.
        :param expansions: Fields for the expansions.
        :param media_fields: Fields for the media object, Expansion required.
        :param user_fields: Fields for the user object, Expansion required.
        :param tweet_fields: Fields for the tweet object, Expansion required.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and up to 100.
        By default, each page will return 100 results.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """

        args = {
            "dm_event.fields": enf_comma_separated(
                name="dm_event_fields",
                value=dm_event_fields,
            ),
            "event_types": event_types,
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/dm_conversations/{dm_conversation_id}/dm_events",
            params=args,
            cls=md.DirectMessageEvent,
            multi=True,
            return_json=return_json,
        )

    def get_dm_events(
        self,
        *,
        dm_event_fields: Optional[Union[str, List, Tuple]] = None,
        event_types: Optional[str] = None,
        expansions: Optional[Union[str, List, Tuple]] = None,
        media_fields: Optional[Union[str, List, Tuple]] = None,
        user_fields: Optional[Union[str, List, Tuple]] = None,
        tweet_fields: Optional[Union[str, List, Tuple]] = None,
        pagination_token: Optional[str] = None,
        max_results: Optional[int] = None,
        return_json: bool = False,
    ) -> Union[dict, md.Response]:
        """
        Returns a list of Direct Messages for the authenticated user, both sent and received.
        Supports retrieving events from the previous 30 days.

        :param dm_event_fields: Fields for the direct message events.
        :param event_types: Type of Direct Message event to return. In the context of one-to-one conversations,
        only `MessageCreate` is relevant.
        :param expansions: Fields for the expansions.
        :param media_fields: Fields for the media object, Expansion required.
        :param user_fields: Fields for the user object, Expansion required.
        :param tweet_fields: Fields for the tweet object, Expansion required.
        :param pagination_token: Token for the pagination.
        :param max_results: The maximum number of results to be returned per page. Number between 1 and up to 100.
        By default, each page will return 100 results.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """
        args = {
            "dm_event.fields": enf_comma_separated(
                name="dm_event_fields",
                value=dm_event_fields,
            ),
            "event_types": event_types,
            "expansions": enf_comma_separated(name="expansions", value=expansions),
            "media.fields": enf_comma_separated(
                name="media_fields", value=media_fields
            ),
            "user.fields": enf_comma_separated(name="user_fields", value=user_fields),
            "tweet.fields": enf_comma_separated(
                name="tweet_fields", value=tweet_fields
            ),
            "max_results": max_results,
            "pagination_token": pagination_token,
        }
        return self._get(
            url=f"{self.BASE_URL_V2}/dm_events",
            params=args,
            cls=md.DirectMessageEvent,
            multi=True,
            return_json=return_json,
        )

    def create_message_to_participant(
        self,
        participant_id: str,
        *,
        attachments: Optional[List[dict]] = None,
        text: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.DirectMessageCreateResponse]:
        """
        Creates a one-to-one Direct Message and adds it to the one-to-one conversation.

        :param participant_id: The User ID of the account this one-to-one Direct Message is to be sent to.
        :param attachments: A single Media ID being attached to the Direct Message.
        This field is required if text is not present. Only 1 attachment is supported.
        :param text: Text of the Direct Message being created. This field is required if attachments is not present.
        Text messages support up to 10,000 characters.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """
        data = {}
        if attachments is not None:
            data["attachments"] = attachments
        if text is not None:
            data["text"] = text
        resp = self._request(
            url=f"{self.BASE_URL_V2}/dm_conversations/with/{participant_id}/messages",
            verb="POST",
            json=data,
        )
        data = self._parse_response(resp=resp)
        return (
            data
            if return_json
            else md.DirectMessageCreateResponse.new_from_json_dict(data["data"])
        )

    def create_message_to_conversation(
        self,
        dm_conversation_id: str,
        *,
        attachments: Optional[List[dict]] = None,
        text: Optional[str] = None,
        return_json: bool = False,
    ) -> Union[dict, md.DirectMessageCreateResponse]:
        """
        Creates a Direct Message on behalf of an authenticated user, and adds it to the specified conversation.

        :param dm_conversation_id: ID of the conversation to add the Direct Message to.
        Supports both 1-1 and group conversations.
        :param attachments: A single Media ID being attached to the Direct Message.
        This field is required if text is not present. Only 1 attachment is supported.
        :param text: Text of the Direct Message being created. This field is required if attachments is not present.
        Text messages support up to 10,000 characters.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """
        data = {}
        if attachments is not None:
            data["attachments"] = attachments
        if text is not None:
            data["text"] = text
        resp = self._request(
            url=f"{self.BASE_URL_V2}/dm_conversations/{dm_conversation_id}/messages",
            verb="POST",
            json=data,
        )
        data = self._parse_response(resp=resp)
        return (
            data
            if return_json
            else md.DirectMessageCreateResponse.new_from_json_dict(data["data"])
        )

    def create_conversation(
        self,
        conversation_type: Optional[str],
        message: Optional[dict],
        participant_ids: Optional[List[str]],
        *,
        return_json: bool = False,
    ) -> Union[dict, md.DirectMessageCreateResponse]:
        """
        Creates a new group conversation and adds a Direct Message to it on behalf of an authenticated user.

        :param conversation_type: Must be set to "Group" (case sensitive).
        :param message: A JSON object that contains either or both the text and attachments parameters.
        :param participant_ids: An array of User IDs that the conversation is created with.
        Conversations can have up to 50 participants.
        :param return_json: Type for returned data. If you set True JSON data will be returned.
        :return: Response instance or json.
        """
        resp = self._request(
            url=f"{self.BASE_URL_V2}/dm_conversations",
            verb="POST",
            json={
                "conversation_type": conversation_type,
                "message": message,
                "participant_ids": participant_ids,
            },
        )
        data = self._parse_response(resp=resp)
        return (
            data
            if return_json
            else md.DirectMessageCreateResponse.new_from_json_dict(data["data"])
        )
