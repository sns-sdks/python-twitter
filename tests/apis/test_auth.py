"""
    tests for auth
"""
import pytest
import responses

from pytwitter import Api, PyTwitterError


@responses.activate
def test_generate_bearer_token(api, helpers):
    token_data = helpers.load_json_data("testdata/apis/authflow/bearer_token.json")

    responses.add(
        responses.POST, url="https://api.twitter.com/oauth2/token", json=token_data
    )

    # test initial by app
    Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        application_only_auth=True,
    )

    # test generate by hand
    resp = api.generate_bearer_token(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
    )
    assert (
        resp["access_token"]
        == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%2FAAAAAAAAAAAAAAAAAAAA%3DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )


@responses.activate
def test_invalidate_bearer_token(api, helpers):
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%2FAAAAAAAAAAAAAAAAAAAA%3DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    token_data = helpers.load_json_data("testdata/apis/authflow/invalidate_token.json")

    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth2/invalidate_token",
        json=token_data,
    )

    resp = api.invalidate_bearer_token(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token=bearer_token,
    )

    assert resp["access_token"] == bearer_token


def test_user_auth():
    with pytest.raises(PyTwitterError):
        Api()

    # initial api
    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="uid-token",
        access_secret="access secret",
    )

    # test for replace auth
    api._auth = None
    with pytest.raises(PyTwitterError):
        api.get_user(user_id="123456")


@responses.activate
def test_oauth_flow():
    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth/request_token",
        json={
            "oauth_token": "uid-token",
            "oauth_token_secret": "oauth token secret",
            "oauth_callback_confirmed": True,
        },
    )

    api = Api(
        consumer_key="consumer key", consumer_secret="consumer secret", oauth_flow=True
    )

    assert api.get_authorize_url()

    # do authorize

    resp_url = "https://localhost/?oauth_token=oauth_token&oauth_token_secret=oauth_token_secret&oauth_verifier=oauth_verifier"

    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth/access_token",
        json={
            "oauth_token": "uid-token",
            "oauth_token_secret": "oauth token secret",
            "user_id": "123456",
        },
    )

    token = api.generate_access_token(response=resp_url)

    assert token["oauth_token"] == "uid-token"
    assert api.auth_user_id == "123456"

    with pytest.raises(PyTwitterError):
        api = Api(
            consumer_key="consumer key",
            consumer_secret="consumer secret",
            oauth_flow=True,
        )
        api.generate_access_token(resp_url)


@responses.activate
def test_oauth_uid():
    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth/request_token",
        json={
            "oauth_token": "uid-token",
            "oauth_token_secret": "oauth token secret",
            "oauth_callback_confirmed": True,
        },
    )
    api = Api(
        consumer_key="consumer key", consumer_secret="consumer secret", oauth_flow=True
    )
    assert api.get_authorize_url()
    # do authorize
    resp_url = "https://localhost/?oauth_token=oauth_token&oauth_token_secret=oauth_token_secret&oauth_verifier=oauth_verifier"

    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth/access_token",
        json={
            "oauth_token": "uid-token",
            "oauth_token_secret": "oauth token secret",
        },
    )

    token = api.generate_access_token(response=resp_url)

    assert token["oauth_token"] == "uid-token"
    assert api.auth_user_id == "uid"


@responses.activate
def test_invalidate_access_token():
    # test revoke bearer token
    api_bearer = Api(bearer_token="token")
    with pytest.raises(PyTwitterError):
        api_bearer.invalidate_access_token()

    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="uid-token",
        access_secret="access secret",
    )
    responses.add(
        responses.POST,
        url="https://api.twitter.com/1.1/oauth/invalidate_token",
        json={"access_token": "ACCESS_TOKEN"},
    )

    resp = api.invalidate_access_token()
    assert resp["access_token"] == "ACCESS_TOKEN"

    # test no auth
    api._auth = None
    with pytest.raises(PyTwitterError):
        api.invalidate_access_token()


@responses.activate
def test_oauth2_flow():
    api = Api(client_id="You client id", oauth_flow=True)

    url, _, code_verifier = api.get_oauth2_authorize_url()
    assert url

    # do authorize

    resp_url = "https://localhost/?state=state&code=code"

    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/oauth2/token",
        json={
            "token_type": "bearer",
            "expires_in": 7200,
            "access_token": "access_token",
            "scope": "users.read tweet.read",
            "expires_at": 1631766428,
        },
    )

    token = api.generate_oauth2_access_token(
        response=resp_url, code_verifier=code_verifier
    )

    assert token["access_token"] == "access_token"

    with pytest.raises(PyTwitterError):
        api = Api(
            consumer_key="consumer key",
            consumer_secret="consumer secret",
            oauth_flow=True,
        )
        api.get_oauth2_authorize_url(resp_url)
