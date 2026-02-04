"""Generated object model: feature.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfFeature(OcsfEntity):
    """Feature.

    The Feature object provides information about the software product
    feature that generated a specific event. It encompasses details related
    to the capabilities, components, user interface (UI) design, and
    performance upgrades associated with the feature.

    Inheritance chain: feature -> _entity -> object
    """
    __tablename__ = "ocsf_feature"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "feature"}

    # Attributes
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the feature.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the feature.",
        nullable=True,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The version of the feature.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfFeature(id={self.id})>"