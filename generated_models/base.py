"""Base classes for OCSF SQLAlchemy models.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Integer,
    BigInteger,
    Float,
    Boolean,
    DateTime,
    LargeBinary,
    Uuid,
    Table,
    Column,
    func,
)
from sqlalchemy.dialects.postgresql import INET, CIDR
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class OcsfBase(DeclarativeBase):
    """Base class for all OCSF SQLAlchemy models.

    Provides:
    - Common table arguments
    - Standard timestamp columns
    - PostgreSQL schema support
    """
    pass


class OcsfTimestampMixin:
    """Mixin providing standard timestamp columns.

    All OCSF tables include created_at and updated_at for audit purposes.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )