"""Generated association model: ocsf_remediation_cis_controls.

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


ocsf_remediation_cis_controls = Table(
    "ocsf_remediation_cis_controls",
    OcsfBase.metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "remediation_id",
        Integer,
        ForeignKey("ocsf_remediation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column(
        "cis_control_id",
        Integer,
        ForeignKey("ocsf_cis_control.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("position", Integer, nullable=True, comment="Order in the array"),
    comment="Association table for remediation.cis_controls",
)