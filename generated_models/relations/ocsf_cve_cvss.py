"""Generated association model: ocsf_cve_cvss.

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


ocsf_cve_cvss = Table(
    "ocsf_cve_cvss",
    OcsfBase.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "cve_id",
        Integer,
        ForeignKey("ocsf_cve.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "cvss_id",
        Integer,
        ForeignKey("ocsf_cvss.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("position", Integer, nullable=True, comment="Order in the array"),
    comment="Association table for cve.cvss",
)