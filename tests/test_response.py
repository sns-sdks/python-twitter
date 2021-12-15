"""
    Tests for response parser.
"""

import pytest

import responses
from pytwitter import PyTwitterError


@responses.activate
def test_parser_response_no_json(api):
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users/123",
        body="",
    )
    with pytest.raises(PyTwitterError):
        api.get_user(user_id="123")


@responses.activate
def test_parser_response_not_ok(api):
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users/123",
        json={
            "title": "Unauthorized",
            "type": "about:blank",
            "status": 401,
            "detail": "Unauthorized",
        },
        status=400,
    )
    with pytest.raises(PyTwitterError):
        api.get_user(user_id="123")


@responses.activate
def test_parser_response_have_error(api):
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users/123",
        json={
            "errors": {
                "title": "Unauthorized",
                "type": "about:blank",
                "status": 401,
                "detail": "Unauthorized",
            }
        },
    )
    with pytest.raises(PyTwitterError):
        api.get_user(user_id="123")


@responses.activate
def test_parser_response_have_reason_error(api):
    # Refer: https://developer.twitter.com/en/support/twitter-api/error-troubleshooting
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users/123",
        json={
            "client_id": "101010101",
            "required_enrollment": "Standard Basic",
            "registration_url": "https://developer.twitter.com/en/account",
            "title": "Client Forbidden",
            "detail": "This request must be made using an approved developer account that is enrolled in the requested endpoint. Learn more by visiting our documentation.",
            "reason": "client-not-enrolled",
            "type": "https://api.twitter.com/2/problems/client-forbidden",
        },
    )
    with pytest.raises(PyTwitterError):
        api.get_user(user_id="123")
