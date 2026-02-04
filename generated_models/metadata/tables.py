"""OCSF metadata tables for runtime documentation.

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


class OcsfMetadataObjects(OcsfBase, OcsfTimestampMixin):
    """Registry of OCSF objects and event classes.

    Stores metadata about each object/event type in the schema.
    """
    __tablename__ = "ocsf_metadata_objects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="Object/event name")
    caption: Mapped[str] = mapped_column(String(200), nullable=False, comment="Human-readable caption")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Full description")
    object_type: Mapped[str] = mapped_column(String(50), nullable=False, comment="Type: object or event")
    extends: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Parent object/event name")
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Event category")
    uid: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Event class UID")

    def __repr__(self) -> str:
        return f"<OcsfMetadataObjects(name='{self.name}')>"


class OcsfMetadataAttributes(OcsfBase, OcsfTimestampMixin):
    """Registry of OCSF attributes.

    Stores metadata about each attribute definition.
    """
    __tablename__ = "ocsf_metadata_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Attribute name")
    object_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Parent object name")
    caption: Mapped[str] = mapped_column(String(200), nullable=False, comment="Human-readable caption")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Full description")
    ocsf_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="OCSF type (e.g., string_t)")
    requirement: Mapped[str] = mapped_column(String(20), default="optional", comment="optional/required/recommended")
    is_array: Mapped[bool] = mapped_column(Boolean, default=False, comment="Whether this is an array")
    is_inherited: Mapped[bool] = mapped_column(Boolean, default=False, comment="Whether inherited from parent")
    source_object: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Object where originally defined")

    def __repr__(self) -> str:
        return f"<OcsfMetadataAttributes(name='{self.name}', object='{self.object_name}')>"


class OcsfMetadataEnums(OcsfBase, OcsfTimestampMixin):
    """Registry of OCSF enum values.

    Stores ID -> caption mappings for all enums.
    """
    __tablename__ = "ocsf_metadata_enums"

    id: Mapped[int] = mapped_column(primary_key=True)
    enum_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="Enum name")
    value_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="Enum value ID")
    caption: Mapped[str] = mapped_column(String(200), nullable=False, comment="Human-readable caption")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Value description")

    def __repr__(self) -> str:
        return f"<OcsfMetadataEnums(enum='{self.enum_name}', value_id={self.value_id})>"


class OcsfMetadataCategories(OcsfBase, OcsfTimestampMixin):
    """Registry of OCSF event categories.

    Stores the 8 event categories and their metadata.
    """
    __tablename__ = "ocsf_metadata_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="Category name")
    caption: Mapped[str] = mapped_column(String(100), nullable=False, comment="Human-readable caption")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Full description")
    uid: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, comment="Category UID")

    def __repr__(self) -> str:
        return f"<OcsfMetadataCategories(name='{self.name}', uid={self.uid})>"


class OcsfMetadataEventClasses(OcsfBase, OcsfTimestampMixin):
    """Registry of OCSF event classes.

    Stores event class UIDs and their mapping to categories.
    """
    __tablename__ = "ocsf_metadata_event_classes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="Event class name")
    caption: Mapped[str] = mapped_column(String(200), nullable=False, comment="Human-readable caption")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Full description")
    uid: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, comment="Event class UID")
    category_uid: Mapped[int] = mapped_column(Integer, nullable=False, comment="Parent category UID")
    extends: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Parent event class")

    def __repr__(self) -> str:
        return f"<OcsfMetadataEventClasses(name='{self.name}', uid={self.uid})>"