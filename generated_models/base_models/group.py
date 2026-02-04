"""Generated object model: group.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfGroup(OcsfEntity):
    """Group.

    The Group object represents a collection or association of entities,
    such as users, policies, or devices. It serves as a logical grouping
    mechanism to organize and manage entities with similar characteristics
    or permissions within a system or organization, including but not
    limited to purposes of access control.

    Inheritance chain: group -> _entity -> object
    """
    __tablename__ = "ocsf_group"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "group"}

    # Attributes
    desc: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The group description.",
        nullable=True,
    )
    domain: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The domain where the group is defined. For example: the LDAP or Active Directory domain.",
        nullable=True,
    )
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The group name.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type of the group or account.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the group. For example, for Windows events this is the security identifier (SID) of the group.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfGroup(id={self.id})>"