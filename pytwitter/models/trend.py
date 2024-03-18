"""
    Trend Object
    Refer: https://developer.twitter.com/en/docs/twitter-api/trends/api-reference/get-trends-by-woeid
"""

from dataclasses import dataclass, field

from .base import BaseModel


@dataclass
class Trend(BaseModel):
    """
    A class representing Trend object
    """

    trend_name: str = field(default=None)
    tweet_count: int = field(default=None)
