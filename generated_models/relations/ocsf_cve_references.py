"""Generated primitive_array model: ocsf_cve_references.

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


class OcsfOcsfCveReferences(OcsfBase):
    """Association table for cve.references.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_cve_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    cve_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_cve.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Values for cve.references",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    cve: Mapped["OcsfCve"] = relationship(
        "OcsfCve",
        back_populates="references",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfCveReferences(id={self.id}, value={self.value})>"