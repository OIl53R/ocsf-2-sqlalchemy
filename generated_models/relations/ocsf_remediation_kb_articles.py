"""Generated primitive_array model: ocsf_remediation_kb_articles.

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


class OcsfOcsfRemediationKbArticles(OcsfBase):
    """Association table for remediation.kb_articles.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_remediation_kb_articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    remediation_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_remediation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Values for remediation.kb_articles",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    remediation: Mapped["OcsfRemediation"] = relationship(
        "OcsfRemediation",
        back_populates="kb_articles",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfRemediationKbArticles(id={self.id}, value={self.value})>"