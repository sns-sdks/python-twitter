"""
    A demo for sample streaming api.
"""

from pytwitter import StreamApi

bearer_token = "your bearer token"


class MyStream(StreamApi):
    def on_tweet(self, tweet):
        print(tweet)


if __name__ == "__main__":
    stream = MyStream(bearer_token=bearer_token)
    stream.sample_stream()
