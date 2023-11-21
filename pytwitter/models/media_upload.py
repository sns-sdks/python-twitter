"""
    Media upload object

    Refer: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
"""


from dataclasses import dataclass, field

from .base import BaseModel


@dataclass
class MediaUpload(BaseModel):
    pass
