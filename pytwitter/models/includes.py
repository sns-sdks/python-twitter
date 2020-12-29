"""
    Expansions objects

    Refer: https://developer.twitter.com/en/docs/twitter-api/expansions
"""
from dataclasses import dataclass, field
from typing import List, Optional

from . import BaseModel, Media, Place, Poll, Tweet, User


@dataclass
class Meta(BaseModel):
    """
    A class representing the meta object for request.
    """

    result_count: Optional[int] = field(default=None)
    previous_token: Optional[str] = field(default=None, repr=False)
    next_token: Optional[str] = field(default=None, repr=False)


@dataclass
class Includes(BaseModel):
    """
    A class representing the expansions object for main request thread.
    """

    media: Optional[List[Media]] = field(default=None, compare=False)
    places: Optional[List[Place]] = field(default=None, compare=False)
    polls: Optional[List[Poll]] = field(default=None, compare=False)
    tweets: Optional[List[Tweet]] = field(default=None, compare=False)
    users: Optional[List[User]] = field(default=None, compare=False)
    meta: Optional[Meta] = field(default=None, compare=False)
