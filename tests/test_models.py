"""
    data model tests
"""

import pytwitter.models as models


def test_user(helpers):
    user_data = helpers.load_json_data("testdata/models/user.json")
    user = models.User.new_from_json_dict(user_data)

    assert user.id == "2244994945"
    assert user.verified
    assert user.public_metrics.followers_count == 510710
    assert user.entities.url.urls[0].url == "https://t.co/3ZX3TNiZCY"
    assert user.entities.description.hashtags[0].tag == "TwitterDev"


def test_tweet(helpers):
    tweet_data = helpers.load_json_data("testdata/models/tweet.json")
    tweet = models.Tweet.new_from_json_dict(tweet_data)

    assert tweet.id == "1212092628029698048"
    assert not tweet.possibly_sensitive
    assert tweet.referenced_tweets[0].id == "1212092627178287104"
    assert tweet.entities.urls[0].url == "https://t.co/yvxdK6aOo2"
    assert tweet.entities.annotations[0].type == "Product"
    assert tweet.public_metrics.like_count == 40
    assert tweet.attachments.media_keys[0] == "16_1211797899316740096"
    assert len(tweet.context_annotations) == 5
    assert tweet.context_annotations[0].domain.id == "119"
    assert tweet.context_annotations[0].entity.name == "New Years Eve"


def test_media(helpers):
    media_data = helpers.load_json_data("testdata/models/media.json")
    media = models.Media.new_from_json_dict(media_data)

    assert media.media_key == "13_1263145212760805376"
    assert media.duration_ms == 46947
    assert media.public_metrics.view_count == 6909260
