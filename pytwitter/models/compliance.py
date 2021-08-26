"""
    Models for compliance
"""

from dataclasses import dataclass, field
from typing import Optional

from .base import BaseModel


@dataclass
class ComplianceJob(BaseModel):
    """
    A class representing the job for compliance.

    Refer: https://developer.twitter.com/en/docs/twitter-api/compliance/batch-compliance/api-reference/get-compliance-jobs-id
    """

    id: Optional[str] = field(default=None)
    created_at: Optional[str] = field(default=None, repr=False)
    type: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None, repr=False)
    upload_url: Optional[str] = field(default=None, repr=False)
    upload_expires_at: Optional[str] = field(default=None, repr=False)
    download_url: Optional[str] = field(default=None, repr=False)
    download_expires_at: Optional[str] = field(default=None, repr=False)
    resumable: Optional[bool] = field(default=None, repr=False)
    status: Optional[str] = field(default=None)
