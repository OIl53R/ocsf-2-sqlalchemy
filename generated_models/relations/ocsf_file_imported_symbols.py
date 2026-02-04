"""Generated primitive_array model: ocsf_file_imported_symbols.

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


class OcsfOcsfFileImportedSymbols(OcsfBase):
    """Association table for file.imported_symbols.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_file_imported_symbols"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_file.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Values for file.imported_symbols",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    file: Mapped["OcsfFile"] = relationship(
        "OcsfFile",
        back_populates="imported_symbols",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfFileImportedSymbols(id={self.id}, value={self.value})>"