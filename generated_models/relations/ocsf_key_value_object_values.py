"""Generated primitive_array model: ocsf_key_value_object_values.

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


class OcsfOcsfKeyValueObjectValues(OcsfBase):
    """Association table for key_value_object.values.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_key_value_object_values"

    id: Mapped[int] = mapped_column(primary_key=True)
    key_value_object_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_key_value_object.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Values for key_value_object.values",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    key_value_object: Mapped["OcsfKeyValueObject"] = relationship(
        "OcsfKeyValueObject",
        back_populates="values",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfKeyValueObjectValues(id={self.id}, value={self.value})>"