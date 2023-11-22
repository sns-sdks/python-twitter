"""
    Usage object
    Refer:https://developer.twitter.com/en/docs/twitter-api/usage/tweets/api-reference/get-usage-tweets
"""

from dataclasses import dataclass, field
from typing import Optional, List

from .base import BaseModel


@dataclass
class UsageUsage(BaseModel):
    date: Optional[str] = field(default=None)
    usage: Optional[str] = field(default=None)


@dataclass
class DailyProjectUsage(BaseModel):
    project_id: Optional[str] = field(default=None)
    usage: Optional[List[UsageUsage]] = field(default=None, repr=False)


@dataclass
class DailyClientAppUsage(BaseModel):
    client_app_id: Optional[str] = field(default=None)
    usage_result_count: Optional[int] = field(default=None)
    usage: Optional[List[UsageUsage]] = field(default=None, repr=False)


@dataclass
class Usage(BaseModel):
    cap_reset_day: Optional[int] = field(default=None)
    project_id: Optional[str] = field(default=None)
    project_cap: Optional[str] = field(default=None)
    project_usage: Optional[str] = field(default=None)
    daily_project_usage: Optional[DailyProjectUsage] = field(default=None, repr=False)
    daily_client_app_usage: Optional[List[DailyClientAppUsage]] = field(
        default=None, repr=False
    )
