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
    assert len(repr(tweet)) < 100
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


def test_poll(helpers):
    poll_data = helpers.load_json_data("testdata/models/poll.json")
    poll = models.Poll.new_from_json_dict(poll_data)

    assert poll.id == "1199786642468413448"
    assert poll.duration_minutes == 1440
    assert len(poll.options) == 2
    assert poll.options[0].position == 1


def test_place(helpers):
    place_data = helpers.load_json_data("testdata/models/place.json")
    place = models.Place.new_from_json_dict(place_data)

    assert place.id == "01a9a39529b27f36"
    assert place.geo.type == "Feature"
    assert len(place.geo.bbox) == 4
    assert place.geo.properties.name == "Dinagat Islands"


def test_rule(helpers):
    rule_data = helpers.load_json_data("testdata/models/rule.json")
    rule = models.StreamRule.new_from_json_dict(rule_data)

    assert rule.id == "1273636687768285187"


def test_includes(helpers):
    includes_none = models.Includes.new_from_json_dict(None)
    assert includes_none is None

    includes_data = helpers.load_json_data("testdata/models/expansions.json")
    includes = models.Includes.new_from_json_dict(includes_data)

    assert len(includes.media) == 1
    assert len(includes.users) == 1
    assert includes.tweets[0].author_id == "2244994945"
    assert len(includes.polls[0].options) == 2
    assert includes.places[0].id == "01a9a39529b27f36"


def test_meta(helpers):
    meta_data = helpers.load_json_data("testdata/models/meta.json")
    meta = models.Meta.new_from_json_dict(meta_data)

    assert meta.result_count == 5
    assert meta.previous_token == "MEOAT4U0J64UGZZZ"

    stream_meta_data = helpers.load_json_data("testdata/models/meta_stream.json")
    stream_meta = models.Meta.new_from_json_dict(stream_meta_data)

    assert stream_meta.sent == "2020-06-18T15:20:24.063Z"
    assert stream_meta.summary.valid == 2


def test_space(helpers):
    space_data = helpers.load_json_data("testdata/models/space.json")
    space = models.Space.new_from_json_dict(space_data)

    assert space.id == "1zqKVXPQhvZJB"
    assert space.participant_count == 420
