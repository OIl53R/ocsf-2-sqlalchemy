"""Generated object model: key_value_object.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfKeyValueObject(OcsfObject):
    """Key:Value object.

    A generic object allowing to define a <code>{key:value}</code> pair.

    Inheritance chain: key_value_object -> object
    """
    __tablename__ = "ocsf_key_value_object"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "key_value_object"}

    # Attributes
    name: Mapped[str] = mapped_column(
        Text,
        comment="The name of the key.",
        nullable=False,
    )
    value: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The value associated to the key.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfKeyValueObject(id={self.id})>"