"""Generated association model: ocsf_remediation_kb_article_list.

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


ocsf_remediation_kb_article_list = Table(
    "ocsf_remediation_kb_article_list",
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
        "kb_article_id",
        Integer,
        ForeignKey("ocsf_kb_article.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),
    Column("position", Integer, nullable=True, comment="Order in the array"),
    comment="Association table for remediation.kb_article_list",
)