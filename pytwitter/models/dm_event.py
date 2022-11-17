"""
    Direct Message events

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/dm-events
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseModel


@dataclass
class DMEReferencedTweet(BaseModel):
    id: Optional[str] = field(default=None)


@dataclass
class DMEAttachments(BaseModel):
    media_keys: Optional[List[str]] = field(default=None)


@dataclass
class DirectMessageEvent(BaseModel):
    """
    A class representing direct message event object.
    """

    id: Optional[str] = field(default=None)
    event_type: Optional[str] = field(default=None)
    text: Optional[str] = field(default=None)
    sender_id: Optional[str] = field(default=None, repr=False)
    participant_id: Optional[List[str]] = field(default=None, repr=False)
    dm_conversation_id: Optional[str] = field(default=None, repr=False)
    created_at: Optional[str] = field(default=None, repr=False)
    referenced_tweets: Optional[List[DMEReferencedTweet]] = field(
        default=None, repr=False
    )


@dataclass
class DirectMessageCreateResponse(BaseModel):
    dm_conversation_id: Optional[str] = field(default=None)
    dm_event_id: Optional[str] = field(default=None)
