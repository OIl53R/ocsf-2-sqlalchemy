"""Generated object model: affected_code.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .file import OcsfFile
from .remediation import OcsfRemediation
from .rule import OcsfRule
from .user import OcsfUser
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfAffectedCode(OcsfObject):
    """Affected Code.

    The Affected Code object describes details about a code block identified
    as vulnerable.

    Inheritance chain: affected_code -> object
    """
    __tablename__ = "ocsf_affected_code"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "affected_code"}

    # Attributes
    end_column: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The column number of the last part of the assessed code identified as vulnerable.",
        nullable=True,
    )
    end_line: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The line number of the last line of code block identified as vulnerable.",
        nullable=True,
    )
    file_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_file.id", ondelete="SET NULL"),
        comment="Details about the file that contains the affected code block.",
        nullable=False,
    )
    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_user.id", ondelete="SET NULL"),
        comment="Details about the user that owns the affected file.",
        nullable=True,
    )
    remediation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_remediation.id", ondelete="SET NULL"),
        comment="Describes the recommended remediation steps to address identified issue(s).",
        nullable=True,
    )
    rule_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_rule.id", ondelete="SET NULL"),
        comment="Details about the specific rule, e.g., those defined as part of a larger <code>policy</code>, that triggered the finding.",
        nullable=True,
    )
    start_column: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The column number of the first part of the assessed code identified as vulnerable.",
        nullable=True,
    )
    start_line: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The line number of the first line of code block identified as vulnerable.",
        nullable=True,
    )

    # Relationships
    file: Mapped[Optional["OcsfFile"]] = relationship(
        "OcsfFile",
        foreign_keys=[file_id],
        back_populates="affected_codes",
    )
    owner: Mapped[Optional["OcsfUser"]] = relationship(
        "OcsfUser",
        foreign_keys=[owner_id],
        back_populates="affected_codes",
    )
    remediation: Mapped[Optional["OcsfRemediation"]] = relationship(
        "OcsfRemediation",
        foreign_keys=[remediation_id],
        back_populates="affected_codes",
    )
    rule: Mapped[Optional["OcsfRule"]] = relationship(
        "OcsfRule",
        foreign_keys=[rule_id],
        back_populates="affected_codes",
    )

    def __repr__(self) -> str:
        return f"<OcsfAffectedCode(id={self.id})>"