"""Generated object model: _entity.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfEntity(OcsfObject):
    """Entity.

    The Entity object is an unordered collection of attributes, with a name
    and unique identifier. It serves as a base object that defines a set of
    attributes and default constraints available in all objects that extend
    it.

    Inheritance chain: _entity -> object
    """
    __tablename__ = "ocsf_entity"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "entity"}

    # Attributes
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the entity.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the entity.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfEntity(id={self.id})>"