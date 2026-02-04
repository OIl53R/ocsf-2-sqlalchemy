"""Generated association model: ocsf_cvss_metrics.

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


ocsf_cvss_metrics = Table(
    "ocsf_cvss_metrics",
    OcsfBase.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "cvss_id",
        Integer,
        ForeignKey("ocsf_cvss.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "metric_id",
        Integer,
        ForeignKey("ocsf_metric.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("position", Integer, nullable=True, comment="Order in the array"),
    comment="Association table for cvss.metrics",
)