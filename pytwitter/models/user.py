"""
    user object

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseModel


@dataclass
class UserEntitiesUrlObj(BaseModel):
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    url: Optional[str] = field(default=None)
    expanded_url: Optional[str] = field(default=None, repr=False)
    display_url: Optional[str] = field(default=None, repr=False)


@dataclass
class UserEntitiesHashtag(BaseModel):
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    tag: Optional[str] = field(default=None)


@dataclass
class UserEntitiesMention(UserEntitiesHashtag):
    ...


@dataclass
class UserEntitiesDescription(BaseModel):
    urls: Optional[List[UserEntitiesUrlObj]] = field(default=None, repr=False)
    hashtags: Optional[List[UserEntitiesHashtag]] = field(default=None, repr=False)
    mentions: Optional[List[UserEntitiesMention]] = field(default=None, repr=False)
    cashtags: Optional[List[UserEntitiesHashtag]] = field(default=None, repr=False)


@dataclass
class UserEntitiesUrl(BaseModel):
    urls: Optional[List[UserEntitiesUrlObj]] = field(default=None)


@dataclass
class UserEntities(BaseModel):
    url: Optional[UserEntitiesUrl] = field(default=None)
    description: Optional[UserEntitiesDescription] = field(default=None, repr=False)


@dataclass
class PublicMetrics(BaseModel):
    followers_count: Optional[int] = field(default=None)
    following_count: Optional[int] = field(default=None)
    tweet_count: Optional[int] = field(default=None, repr=False)
    listed_count: Optional[int] = field(default=None, repr=False)


@dataclass
class UserWithheld(BaseModel):
    """
    refer: https://help.twitter.com/en/rules-and-policies/tweet-withheld-by-country
    """

    scope: Optional[str] = field(default=None)
    country_codes: Optional[List[str]] = field(default=None, repr=False)


@dataclass
class User(BaseModel):
    """
    A class representing the user object.
    """

    id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None, compare=False)
    username: Optional[str] = field(default=None, compare=False)
    created_at: Optional[str] = field(default=None, repr=False, compare=False)
    description: Optional[str] = field(default=None, repr=False, compare=False)
    location: Optional[str] = field(default=None, repr=False, compare=False)
    pinned_tweet_id: Optional[str] = field(default=None, repr=False, compare=False)
    profile_image_url: Optional[str] = field(default=None, repr=False, compare=False)
    protected: Optional[bool] = field(default=None, repr=False, compare=False)
    url: Optional[str] = field(default=None, repr=False, compare=False)
    verified: Optional[bool] = field(default=None, repr=False, compare=False)
    entities: Optional[UserEntities] = field(default=None, repr=False, compare=False)
    public_metrics: Optional[PublicMetrics] = field(
        default=None, repr=False, compare=False
    )
    withheld: Optional[UserWithheld] = field(default=None, repr=False, compare=False)
