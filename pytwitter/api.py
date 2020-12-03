"""
    Api Impl
"""

import requests
from requests_oauthlib import OAuth2


class Api:
    def __init__(
            self,
            bearer_token=None,
            consumer_key=None,
            consumer_secret=None,
            access_token=None,
            access_secret=None,
            application_only_auth=False,
            oauth_flow=False,
    ):
        self.session = requests.Session()
        self.__auth = None

        # just use bearer token
        if bearer_token:
            self.__auth = OAuth2(token={
                "Bearer": bearer_token
            })
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
        if enforce_auth:
            if not self.__auth:
                raise Exception("The twitter.Api instance must be authenticated.")
