"""
    Tests for media upload API v2
"""

import pytest
import responses

from pytwitter import PyTwitterError


@responses.activate
def test_media_upload_simple_v2(api_with_user, helpers):
    with pytest.raises(PyTwitterError):
        api_with_user.upload_media_simple_v2()

    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/media/upload",
        json=helpers.load_json_data(
            "testdata/apis/media_upload_v2/upload_simple_resp.json"
        ),
    )

    with open("testdata/apis/media_upload/x-logo.png", "rb") as media:
        resp = api_with_user.upload_media_simple_v2(
            media=media,
            media_category="tweet_image",
            additional_owners=["123456789"],
        )
        assert resp.id == "1726817595448610817"

    with open("testdata/apis/media_upload/x-logo.png", "rb") as media:
        resp = api_with_user.upload_media_simple_v2(
            media=media, media_category="tweet_image", return_json=True
        )
        assert resp["id"] == "1726817595448610817"


@responses.activate
def test_upload_media_chunked_init_v2(api_with_user, helpers):
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/media/upload/initialize",
        json=helpers.load_json_data(
            "testdata/apis/media_upload_v2/upload_chunk_init_resp.json"
        ),
    )

    resp = api_with_user.upload_media_chunked_init_v2(
        total_bytes=1000000,
        media_type="video/mp4",
        media_category="tweet_video",
        additional_owners=["123456789"],
    )
    assert resp.data.id == "1912103767639719936"

    resp_json = api_with_user.upload_media_chunked_init_v2(
        total_bytes=1000000,
        media_type="video/mp4",
        return_json=True,
    )
    assert resp_json["data"]["id"] == "1912103767639719936"


@responses.activate
def test_upload_media_chunked_append_v2(api_with_user, helpers):
    media_id = "1912090619981471744"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/media/upload/{media_id}/append",
    )

    with open("testdata/apis/media_upload/x-logo.png", "rb") as media:
        segment_index = 0
        while True:
            chunk = media.read(1 * 1024 * 1024)
            if not chunk:
                break
            status = api_with_user.upload_media_chunked_append_v2(
                media_id=media_id,
                media=media,
                segment_index=segment_index,
            )
            assert status

            segment_index += 1

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/media/upload/{media_id}/append",
        status=401,
        json={"errors": [{"code": 32, "message": "Could not authenticate you."}]},
    )
    with pytest.raises(PyTwitterError):
        api_with_user.upload_media_chunked_append_v2(
            media_id=media_id,
            media=b"",
            segment_index=1,
        )


@responses.activate
def test_upload_media_chunked_finalize_v2(api_with_user, helpers):
    media_id = "1912090619981471744"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/media/upload/{media_id}/finalize",
        json=helpers.load_json_data(
            "testdata/apis/media_upload_v2/upload_chunk_finalize_resp.json"
        ),
    )

    resp = api_with_user.upload_media_chunked_finalize_v2(
        media_id=media_id,
    )
    assert resp.data.id == media_id

    resp_json = api_with_user.upload_media_chunked_finalize_v2(
        media_id=media_id,
        return_json=True,
    )
    assert resp_json["data"]["id"] == media_id


@responses.activate
def test_upload_media_chunked_status_v2(api_with_user, helpers):
    media_id = "1912090619981471744"

    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/media/upload",
        json=helpers.load_json_data(
            "testdata/apis/media_upload_v2/upload_chunk_status_resp.json"
        ),
    )

    resp = api_with_user.upload_media_chunked_status_v2(
        media_id=media_id,
    )
    assert resp.data.processing_info.state == "succeeded"

    resp_json = api_with_user.upload_media_chunked_status_v2(
        media_id=media_id,
        return_json=True,
    )
    assert resp_json["data"]["processing_info"]["state"] == "succeeded"
