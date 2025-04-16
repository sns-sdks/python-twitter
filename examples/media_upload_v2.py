"""
    Upload a video with media upload v2
"""

import os

from pytwitter import Api

consumer_key = "your app consumer key"
consumer_secret = "your app consumer secret"
access_token = "your access token"
access_secret = "your access token secret"

# init api with OAuth1.0
api = Api(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_secret=access_secret,
)

video_path = "path/to/video.mp4"

# init media upload

init_resp = api.upload_media_chunked_init_v2(
    total_bytes=os.path.getsize(video_path),
    media_type="video/mp4",
    media_category="tweet_video",
)

print(f"Init response: {init_resp}")

# upload by chunk
chunk_size = 1024 * 1024 * 1
segment_index = 0

with open(video_path, "rb") as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break

        chunk_resp = api.upload_media_chunked_append_v2(
            media_id=init_resp.data.id,
            segment_index=segment_index,
            media=chunk,
        )
        print(f"Chunk response: {chunk_resp}")

print("Finished chunk upload")

# finalize upload
finalize_resp = api.upload_media_chunked_finalize_v2(
    media_id=init_resp.data.id,
)
print(f"Finalize response: {finalize_resp}")

# Now you can use the media to create tweet
tweet_resp = api.create_tweet(
    text="Tweet with video", media_media_ids=[init_resp.data.id]
)

print(f"Tweet response: {tweet_resp}")
