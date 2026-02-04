"""Generated association model: ocsf_advisory_related_cves.

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


ocsf_advisory_related_cves = Table(
    "ocsf_advisory_related_cves",
    OcsfBase.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "advisory_id",
        Integer,
        ForeignKey("ocsf_advisory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "cve_id",
        Integer,
        ForeignKey("ocsf_cve.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("position", Integer, nullable=True, comment="Order in the array"),
    comment="Association table for advisory.related_cves",
)