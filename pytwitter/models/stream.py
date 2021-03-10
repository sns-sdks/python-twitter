"""
    stream obj.
"""

from dataclasses import dataclass, field
from typing import Optional

from .base import BaseModel


@dataclass
class StreamRule(BaseModel):
    id: Optional[str] = field(default=None)
    value: Optional[str] = field(default=None)
    tag: Optional[str] = field(default=None, repr=False)
