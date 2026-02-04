"""Generated object model: cwe.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfCwe(OcsfObject):
    """CWE.

    The CWE object represents a weakness in a software system that can be
    exploited by a threat actor to perform an attack. The CWE object is
    based on the <a target='_blank' href='https://cwe.mitre.org/'>Common
    Weakness Enumeration (CWE)</a> catalog.

    Inheritance chain: cwe -> object
    """
    __tablename__ = "ocsf_cwe"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "cwe"}

    # Attributes
    caption: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The caption assigned to the Common Weakness Enumeration unique identifier.",
        nullable=True,
    )
    src_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="URL pointing to the CWE Specification. For more information see <a target='_blank' href='https://cwe.mitre.org/'>CWE.</a>",
        nullable=True,
    )
    uid: Mapped[str] = mapped_column(
        Text,
        comment="The Common Weakness Enumeration unique number assigned to a specific weakness. A CWE Identifier begins \"CWE\" followed by a sequence of digits that acts as a unique identifier. For example:...",
        nullable=False,
    )


    def __repr__(self) -> str:
        return f"<OcsfCwe(id={self.id})>"