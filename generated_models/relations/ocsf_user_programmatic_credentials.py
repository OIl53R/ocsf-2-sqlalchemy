"""Generated association model: ocsf_user_programmatic_credentials.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    ForeignKey, String, Text, Integer, BigInteger, Float,
    Boolean, DateTime, LargeBinary, Uuid, Table, Column, func,
)
from sqlalchemy.dialects.postgresql import INET, CIDR
from sqlalchemy.orm import Mapped, mapped_column, relationship


ocsf_user_programmatic_credentials = Table(
    "ocsf_user_programmatic_credentials",
    OcsfBase.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "user_id",
        Integer,
        ForeignKey("ocsf_user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "programmatic_credential_id",
        Integer,
        ForeignKey("ocsf_programmatic_credential.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("position", Integer, nullable=True, comment="Order in the array"),
    comment="Association table for user.programmatic_credentials",
)