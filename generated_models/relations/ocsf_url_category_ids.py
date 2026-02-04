"""Generated primitive_array model: ocsf_url_category_ids.

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


class OcsfOcsfUrlCategoryIds(OcsfBase):
    """Association table for url.category_ids.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_url_category_ids"

    id: Mapped[int] = mapped_column(primary_key=True)
    url_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_url.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Values for url.category_ids",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    url: Mapped["OcsfUrl"] = relationship(
        "OcsfUrl",
        back_populates="category_ids",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfUrlCategoryIds(id={self.id}, value={self.value})>"