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
