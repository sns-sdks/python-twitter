"""
    Media upload response object:

    Refer: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/api-reference/post-media-upload
"""

from dataclasses import dataclass, field
from typing import Optional

from .base import BaseModel


@dataclass
class MediaUploadResponseProcessingInfoError(BaseModel):
    """
    A class representing the media upload response processing info error object.
    """

    code: Optional[int] = field(default=None)
    name: Optional[str] = field(default=None)
    message: Optional[str] = field(default=None)


@dataclass
class MediaUploadResponseProcessingInfo(BaseModel):
    """
    A class representing the media upload response processing info object.
    """

    state: Optional[str] = field(default=None)
    check_after_secs: Optional[int] = field(default=None)
    progress_percent: Optional[int] = field(default=None)
    error: Optional[MediaUploadResponseProcessingInfoError] = field(default=None)


@dataclass
class MediaUploadResponseImage(BaseModel):
    """
    A class representing the media upload response image object.
    """

    image_type: Optional[str] = field(default=None)
    w: Optional[int] = field(default=None)
    h: Optional[int] = field(default=None)


@dataclass
class MediaUploadResponseVideo(BaseModel):
    """
    A class representing the media upload response video object.
    """

    video_type: Optional[str] = field(default=None)


@dataclass
class MediaUploadResponse(BaseModel):
    """
    A class representing the media upload response object.
    """

    media_id: Optional[int] = field(default=None)
    media_id_string: Optional[str] = field(default=None)
    media_key: Optional[str] = field(default=None, repr=False)
    size: Optional[int] = field(default=None, repr=False)
    expires_after_secs: Optional[int] = field(default=None, repr=False)
    processing_info: Optional[MediaUploadResponseProcessingInfo] = field(default=None)
    image: Optional[MediaUploadResponseImage] = field(default=None)
    video: Optional[MediaUploadResponseVideo] = field(default=None)
