"""Generated object model: remediation.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .cis_control import OcsfCisControl
from .kb_article import OcsfKbArticle
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfRemediation(OcsfObject):
    """Remediation.

    The Remediation object describes the recommended remediation steps to
    address identified issue(s).

    Inheritance chain: remediation -> object
    """
    __tablename__ = "ocsf_remediation"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "remediation"}

    # Attributes
    desc: Mapped[str] = mapped_column(
        Text,
        comment="The description of the remediation strategy.",
        nullable=False,
    )

    # Relationships
    cis_controls: Mapped[List["OcsfCisControl"]] = relationship(
        "OcsfCisControl",
        secondary="ocsf_remediation_cis_controls",
        back_populates="remediations",
    )
    kb_article_list: Mapped[List["OcsfKbArticle"]] = relationship(
        "OcsfKbArticle",
        secondary="ocsf_remediation_kb_article_list",
        back_populates="remediations",
    )

    def __repr__(self) -> str:
        return f"<OcsfRemediation(id={self.id})>"