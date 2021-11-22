"""
    A demo for search streaming api.
"""

from pytwitter import StreamApi


bearer_token = "your bearer token"


class MySearchStream(StreamApi):
    def on_tweet(self, tweet):
        print(tweet)


if __name__ == "__main__":
    # Application should be
    stream = MySearchStream(bearer_token=bearer_token)

    # create new rules
    add_rules = {
        "add": [
            {"value": "cat has:media", "tag": "cats with media"},
            {"value": "cat has:media -grumpy", "tag": "happy cats with media"},
        ]
    }

    # validate rules
    stream.manage_rules(rules=add_rules, dry_run=True)

    # create rules
    # Rules remain after creating them, check them using stream.get_rules(return_json=True)
    stream.manage_rules(rules=add_rules)
    # Response(data=[StreamRule(id='1370406958721732610', value='cat has:media -grumpy'), StreamRule(id='1370406958721732609', value='cat has:media')])

    # get tweets
    stream.search_stream()
