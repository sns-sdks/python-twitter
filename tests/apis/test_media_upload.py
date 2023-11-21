"""
    Tests for media upload API
"""
import base64

import pytest
import responses

from pytwitter import PyTwitterError


@responses.activate
def test_media_upload_simple(api_with_user, helpers):
    with pytest.raises(PyTwitterError):
        api_with_user.upload_media_simple()

    responses.add(
        responses.POST,
        url="https://upload.twitter.com/1.1/media/upload.json",
        json=helpers.load_json_data(
            "testdata/apis/media_upload/upload_simple_resp.json"
        ),
    )

    with open("testdata/apis/media_upload/x-logo.png", "rb") as media:
        resp = api_with_user.upload_media_simple(
            media=media,
            media_category="tweet_image",
            additional_owners=["123456789"],
        )
        assert resp.media_id_string == "1726817595448610817"

    with open("testdata/apis/media_upload/x-logo.png", "rb") as f:
        media_data = base64.b64encode(f.read()).decode("utf-8")
        resp_json = api_with_user.upload_media_simple(
            media_data=media_data,
            return_json=True,
        )
        assert resp_json["media_id_string"] == "1726817595448610817"


@responses.activate
def test_upload_media_chunked_init(api_with_user, helpers):
    responses.add(
        responses.POST,
        url="https://upload.twitter.com/1.1/media/upload.json",
        json=helpers.load_json_data(
            "testdata/apis/media_upload/upload_chunk_init_resp.json"
        ),
    )

    resp = api_with_user.upload_media_chunked_init(
        total_bytes=1000000,
        media_type="video/mp4",
        media_category="tweet_video",
        additional_owners=["123456789"],
    )
    assert resp.media_id_string == "1726870404957175808"

    resp_json = api_with_user.upload_media_chunked_init(
        total_bytes=1000000,
        media_type="video/mp4",
        return_json=True,
    )
    assert resp_json["media_id"] == 1726870404957175808


@responses.activate
def test_upload_media_chunked_append(api_with_user, helpers):
    media_id = "1726870404957175808"

    with pytest.raises(PyTwitterError):
        api_with_user.upload_media_chunked_append(media_id=media_id, segment_index=0)

    responses.add(
        responses.POST,
        url="https://upload.twitter.com/1.1/media/upload.json",
    )

    with open("testdata/apis/media_upload/xaa", "rb") as media:
        status = api_with_user.upload_media_chunked_append(
            media_id=media_id,
            media=media,
            segment_index=0,
        )
        assert status

    with open("testdata/apis/media_upload/xab", "rb") as f:
        media_data = base64.b64encode(f.read()).decode("utf-8")
        status = api_with_user.upload_media_chunked_append(
            media_id=media_id,
            media_data=media_data,
            segment_index=1,
        )
        assert status

    responses.add(
        responses.POST,
        url="https://upload.twitter.com/1.1/media/upload.json",
        status=401,
        json={"errors": [{"code": 32, "message": "Could not authenticate you."}]},
    )
    with pytest.raises(PyTwitterError):
        api_with_user.upload_media_chunked_append(
            media_id=media_id,
            media_data=media_data,
            segment_index=1,
        )


@responses.activate
def test_upload_media_chunked_finalize(api_with_user, helpers):
    media_id = "1726870404957175808"

    responses.add(
        responses.POST,
        url="https://upload.twitter.com/1.1/media/upload.json",
        json=helpers.load_json_data(
            "testdata/apis/media_upload/upload_chunk_finalize_resp.json"
        ),
    )

    resp = api_with_user.upload_media_chunked_finalize(
        media_id=media_id,
    )
    assert resp.media_id_string == media_id

    resp_json = api_with_user.upload_media_chunked_finalize(
        media_id=media_id,
        return_json=True,
    )
    assert resp_json["media_id_string"] == media_id


@responses.activate
def test_upload_media_chunked_status(api_with_user, helpers):
    media_id = "1726870404957175808"

    responses.add(
        responses.GET,
        url="https://upload.twitter.com/1.1/media/upload.json",
        json=helpers.load_json_data(
            "testdata/apis/media_upload/upload_chunk_status_resp.json"
        ),
    )

    resp = api_with_user.upload_media_chunked_status(
        media_id=media_id,
    )
    assert resp.processing_info.state == "succeeded"

    resp_json = api_with_user.upload_media_chunked_status(
        media_id=media_id,
        return_json=True,
    )
    assert resp_json["processing_info"]["state"] == "succeeded"
