"""
    tweet object

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
"""
import textwrap
from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseModel
from .stream import StreamRule


@dataclass
class TweetAttachments(BaseModel):
    poll_ids: Optional[List[str]] = field(default=None, repr=False, compare=False)
    media_keys: Optional[List[str]] = field(default=None, repr=False, compare=False)


@dataclass
class TweetContextAnnotationDomain(BaseModel):
    id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetContextAnnotationEntity(BaseModel):
    id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)


@dataclass
class TweetEditControls(BaseModel):
    edits_remaining: Optional[int] = field(default=None)
    is_edit_eligible: Optional[bool] = field(default=None)
    editable_until: Optional[str] = field(default=None)


@dataclass
class TweetContextAnnotation(BaseModel):
    """
    Refer https://developer.twitter.com/en/docs/twitter-api/annotations
    """

    domain: Optional[TweetContextAnnotationDomain] = field(
        default=None, repr=False, compare=False
    )
    entity: Optional[TweetContextAnnotationEntity] = field(
        default=None, repr=False, compare=False
    )


@dataclass
class TweetEntitiesAnnotation(BaseModel):
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    probability: Optional[float] = field(default=None, repr=False)
    type: Optional[str] = field(default=None)
    normalized_text: Optional[str] = field(default=None)


@dataclass
class TweetEntitiesHashtag(BaseModel):
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    tag: Optional[str] = field(default=None)


@dataclass
class TweetEntitiesCashtag(TweetEntitiesHashtag):
    ...


@dataclass
class TweetEntitiesMention(BaseModel):
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    username: Optional[str] = field(default=None)


@dataclass
class TweetEntitiesUrl(BaseModel):
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    url: Optional[str] = field(default=None)
    expanded_url: Optional[str] = field(default=None, repr=False)
    display_url: Optional[str] = field(default=None, repr=False)
    status: Optional[str] = field(default=None, repr=False)
    title: Optional[str] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    unwound_url: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetEntities(BaseModel):
    annotations: Optional[List[TweetEntitiesAnnotation]] = field(
        default=None, repr=False
    )
    cashtags: Optional[List[TweetEntitiesCashtag]] = field(default=None, repr=False)
    hashtags: Optional[List[TweetEntitiesHashtag]] = field(default=None, repr=False)
    mentions: Optional[List[TweetEntitiesMention]] = field(default=None, repr=False)
    urls: Optional[List[TweetEntitiesUrl]] = field(default=None, repr=False)


@dataclass
class TweetGeoCoordinates(BaseModel):
    type: Optional[str] = field(default=None)
    coordinates: Optional[List[float]] = field(default=None, repr=False)


@dataclass
class TweetGeo(BaseModel):
    coordinates: Optional[TweetGeoCoordinates] = field(default=None, repr=False)
    place_id: Optional[str] = field(default=None)


@dataclass
class TweetNonPublicMetrics(BaseModel):
    impression_count: Optional[int] = field(default=None)
    url_link_clicks: Optional[int] = field(default=None, repr=False)
    user_profile_clicks: Optional[int] = field(default=None, repr=False)


@dataclass
class TweetOrganicMetrics(TweetNonPublicMetrics):
    like_count: Optional[int] = field(default=None, repr=False)
    reply_count: Optional[int] = field(default=None, repr=False)
    retweet_count: Optional[int] = field(default=None, repr=False)


@dataclass
class TweetPromotedMetrics(TweetOrganicMetrics):
    ...


@dataclass
class TweetPublicMetrics(BaseModel):
    retweet_count: Optional[int] = field(default=None, repr=False)
    quote_count: Optional[int] = field(default=None, repr=False)
    reply_count: Optional[int] = field(default=None, repr=False)
    like_count: Optional[int] = field(default=None)


@dataclass
class TweetWithheld(BaseModel):
    """
    refer: https://help.twitter.com/en/rules-and-policies/tweet-withheld-by-country
    """

    copyright: Optional[bool] = field(default=None, repr=False)
    country_codes: Optional[List[str]] = field(default=None, repr=False, compare=False)


@dataclass
class TweetReferencedTweet(BaseModel):
    type: Optional[str] = field(default=None, repr=False, compare=False)
    id: Optional[str] = field(default=None, repr=False, compare=False)


@dataclass
class Tweet(BaseModel):
    """
    A class representing the tweet object.
    """

    id: Optional[str] = field(default=None)
    text: Optional[str] = field(default=None)
    edit_history_tweet_ids: Optional[List[str]] = field(default=None)
    attachments: Optional[TweetAttachments] = field(
        default=None, repr=False, compare=False
    )
    author_id: Optional[str] = field(default=None, repr=False, compare=False)
    context_annotations: Optional[List[TweetContextAnnotation]] = field(
        default=None, repr=False, compare=False
    )
    conversation_id: Optional[str] = field(default=None, repr=False, compare=False)
    created_at: Optional[str] = field(default=None, repr=False, compare=False)
    edit_controls: Optional[TweetEditControls] = field(
        default=None, repr=False, compare=False
    )
    entities: Optional[TweetEntities] = field(default=None, repr=False, compare=False)
    geo: Optional[TweetGeo] = field(default=None, repr=False, compare=False)
    in_reply_to_user_id: Optional[str] = field(default=None, repr=False, compare=False)
    lang: Optional[str] = field(default=None, repr=False, compare=False)
    non_public_metrics: Optional[TweetNonPublicMetrics] = field(
        default=None, repr=False, compare=False
    )
    organic_metrics: Optional[TweetNonPublicMetrics] = field(
        default=None, repr=False, compare=False
    )
    possibly_sensitive: Optional[bool] = field(default=None, repr=False, compare=False)
    promoted_metrics: Optional[TweetPromotedMetrics] = field(
        default=None, repr=False, compare=False
    )
    public_metrics: Optional[TweetPublicMetrics] = field(
        default=None, repr=False, compare=False
    )
    referenced_tweets: Optional[List[TweetReferencedTweet]] = field(
        default=None, repr=False, compare=False
    )
    reply_settings: Optional[str] = field(default=None, repr=False, compare=False)
    source: Optional[str] = field(default=None, repr=False, compare=False)
    withheld: Optional[TweetWithheld] = field(default=None, repr=False, compare=False)

    # Note: this field only for stream tweet
    matching_rules: Optional[List[StreamRule]] = field(
        default=None, repr=False, compare=False
    )

    def __repr__(self):
        text = self.text
        if text:
            # Make text shorter to display.
            text = textwrap.shorten(self.text, width=50, placeholder="...")
        return f"Tweet(id={self.id}, text={text})"
