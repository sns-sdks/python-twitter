"""
    Space object.

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/space
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseModel


@dataclass
class Space(BaseModel):
    """
    A class representing the space object.
    """

    id: Optional[str] = field(default=None)
    state: Optional[str] = field(default=None)
    created_at: Optional[str] = field(default=None, repr=False)
    ended_at: Optional[str] = field(default=None, repr=False)
    host_ids: Optional[List[str]] = field(default=None, repr=False)
    lang: Optional[str] = field(default=None, repr=False)
    is_ticketed: Optional[bool] = field(default=None, repr=False)
    invited_user_ids: Optional[List[str]] = field(default=None, repr=False)
    participant_count: Optional[int] = field(default=None, repr=False)
    subscriber_count: Optional[int] = field(default=None, repr=False)
    scheduled_start: Optional[str] = field(default=None, repr=False)
    speaker_ids: Optional[List[str]] = field(default=None, repr=False)
    started_at: Optional[str] = field(default=None, repr=False)
    title: Optional[str] = field(default=None, repr=False)
    topic_ids: Optional[List[str]] = field(default=None, repr=False)
    updated_at: Optional[str] = field(default=None, repr=False)


@dataclass
class Topic(BaseModel):
    """
    A class representing the space topic object.
    """

    id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None, repr=False)
