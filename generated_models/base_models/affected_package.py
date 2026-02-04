"""Generated object model: affected_package.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .package import OcsfPackage
from .remediation import OcsfRemediation
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfAffectedPackage(OcsfPackage):
    """Affected Software Package.

    The Affected Package object describes details about a software package
    identified as affected by a vulnerability/vulnerabilities.

    Inheritance chain: affected_package -> package -> object
    """
    __tablename__ = "ocsf_affected_package"

    # Joined table inheritance from package
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_package.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "affected_package"}

    # Attributes
    fixed_in_version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The software package version in which a reported vulnerability was patched/fixed.",
        nullable=True,
    )
    path: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The installation path of the affected package.",
        nullable=True,
    )
    remediation_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_remediation.id", ondelete="SET NULL"),
        comment="Describes the recommended remediation steps to address identified issue(s).",
        nullable=True,
    )

    # Relationships
    remediation: Mapped[Optional["OcsfRemediation"]] = relationship(
        "OcsfRemediation",
        foreign_keys=[remediation_id],
        back_populates="affected_packages",
    )

    def __repr__(self) -> str:
        return f"<OcsfAffectedPackage(id={self.id})>"