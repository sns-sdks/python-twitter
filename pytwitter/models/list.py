"""
    Model for list.

    Refer: https://developer.twitter.com/en/docs/twitter-api/lists/manage-lists/api-reference/post-lists
"""

from dataclasses import dataclass, field
from typing import Optional

from .base import BaseModel


@dataclass
class TwitterList(BaseModel):
    id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None, repr=False)
    private: Optional[bool] = field(default=None, repr=False)
