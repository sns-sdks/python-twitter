"""
    Poll object

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/poll
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .base import BaseModel


@dataclass
class PollOption(BaseModel):
    position: Optional[int] = field(default=None, repr=False)
    label: Optional[str] = field(default=None)
    votes: Optional[int] = field(default=None, repr=False)


@dataclass
class Poll(BaseModel):
    """
    A class representing poll object.
    """

    id: Optional[str] = field(default=None)
    options: Optional[List[PollOption]] = field(default=None, repr=False)
    duration_minutes: Optional[int] = field(default=None, repr=False)
    end_datetime: Optional[str] = field(default=None, repr=False)
    voting_status: Optional[str] = field(default=None, repr=False)
