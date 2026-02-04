"""Generated primitive_array model: ocsf_remediation_references.

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


class OcsfOcsfRemediationReferences(OcsfBase):
    """Association table for remediation.references.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_remediation_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    remediation_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_remediation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Values for remediation.references",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    remediation: Mapped["OcsfRemediation"] = relationship(
        "OcsfRemediation",
        back_populates="references",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfRemediationReferences(id={self.id}, value={self.value})>"