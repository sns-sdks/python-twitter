"""
    Media object

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseModel


@dataclass
class MediaNonPublicMetrics(BaseModel):
    playback_0_count: Optional[int] = field(default=None)
    playback_100_count: Optional[int] = field(default=None, repr=False)
    playback_25_count: Optional[int] = field(default=None, repr=False)
    playback_50_count: Optional[int] = field(default=None, repr=False)
    playback_75_count: Optional[int] = field(default=None, repr=False)


@dataclass
class MediaOrganicMetrics(MediaNonPublicMetrics):
    view_count: Optional[int] = field(default=None, repr=False)


@dataclass
class MediaPromotedMetrics(MediaOrganicMetrics):
    ...


@dataclass
class MediaPublicMetrics(BaseModel):
    view_count: Optional[int] = field(default=None, repr=False)


@dataclass
class MediaVariant(BaseModel):
    bit_rate: Optional[int] = field(default=None)
    content_type: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)


@dataclass
class Media(BaseModel):
    """
    A class representing the media object.
    """

    media_key: Optional[str] = field(default=None)
    type: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None, repr=False)
    duration_ms: Optional[int] = field(default=None, repr=False)
    height: Optional[int] = field(default=None, repr=False)
    non_public_metrics: Optional[MediaNonPublicMetrics] = field(
        default=None, repr=False
    )
    organic_metrics: Optional[MediaOrganicMetrics] = field(default=None, repr=False)
    preview_image_url: Optional[str] = field(default=None, repr=False)
    promoted_metrics: Optional[MediaPromotedMetrics] = field(default=None, repr=False)
    public_metrics: Optional[MediaPublicMetrics] = field(default=None, repr=False)
    width: Optional[int] = field(default=None, repr=False)
    alt_text: Optional[str] = field(default=None, repr=False)
    variants: Optional[List[MediaVariant]] = field(default=None, repr=False)
