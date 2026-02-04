"""Generated object model: rule.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfRule(OcsfEntity):
    """Rule.

    The Rule object describes characteristics of a rule associated with a
    policy or an event.

    Inheritance chain: rule -> _entity -> object
    """
    __tablename__ = "ocsf_rule"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "rule"}

    # Attributes
    category: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The rule category.",
        nullable=True,
    )
    desc: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The description of the rule that generated the event.",
        nullable=True,
    )
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the rule that generated the event.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The rule type.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the rule that generated the event.",
        nullable=True,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The rule version. For example: <code>1.1</code>.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfRule(id={self.id})>"