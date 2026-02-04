"""Generated object model: cis_control.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfCisControl(OcsfObject):
    """CIS Control.

    The CIS Control (aka Critical Security Control) object describes a
    prioritized set of actions to protect your organization and data from
    cyber-attack vectors. The <a target='_blank'
    href='https://www.cisecurity.org/controls'>CIS Controls</a> are defined
    by the Center for Internet Security.

    Inheritance chain: cis_control -> object
    """
    __tablename__ = "ocsf_cis_control"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "cis_control"}

    # Attributes
    desc: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The CIS Control description. For example: <i>Uninstall or disable unnecessary services on enterprise assets and software, such as an unused file sharing service, web application module, or service...",
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        Text,
        comment="The CIS Control name. For example: <i>4.8 Uninstall or Disable Unnecessary Services on Enterprise Assets and Software.</i>",
        nullable=False,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The CIS Control version. For example: <i>v8</i>.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfCisControl(id={self.id})>"