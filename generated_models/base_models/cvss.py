"""Generated object model: cvss.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .metric import OcsfMetric
from typing import Optional, List
from sqlalchemy import Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfCvss(OcsfObject):
    """CVSS Score.

    The Common Vulnerability Scoring System (<a target='_blank'
    href='https://www.first.org/cvss/'>CVSS</a>) object provides a way to
    capture the principal characteristics of a vulnerability and produce a
    numerical score reflecting its severity.

    Inheritance chain: cvss -> object
    """
    __tablename__ = "ocsf_cvss"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "cvss"}

    # Attributes
    base_score: Mapped[float] = mapped_column(
        Float,
        comment="The CVSS base score. For example: <code>9.1</code>.",
        nullable=False,
    )
    depth: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The CVSS depth represents a depth of the equation used to calculate CVSS score.",
        nullable=True,
    )
    overall_score: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="The CVSS overall score, impacted by base, temporal, and environmental metrics. For example: <code>9.1</code>.",
        nullable=True,
    )
    severity: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="<p>The Common Vulnerability Scoring System (CVSS) Qualitative Severity Rating. A textual representation of the numeric score.</p><strong>CVSS v2.0</strong><ul><li>Low (0.0 – 3.9)</li><li>Medium...",
        nullable=True,
    )
    src_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The source URL for the CVSS score. For example: <code>https://nvd.nist.gov/vuln/detail/CVE-2021-44228</code>",
        nullable=True,
    )
    vector_string: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The CVSS vector string is a text representation of a set of CVSS metrics. It is commonly used to record or transfer CVSS metric information in a concise form. For example:...",
        nullable=True,
    )
    vendor_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The vendor that provided the CVSS score. For example: <code>NVD, REDHAT</code> etc.",
        nullable=True,
    )
    version: Mapped[str] = mapped_column(
        Text,
        comment="The CVSS version. For example: <code>3.1</code>.",
        nullable=False,
    )

    # Relationships
    metrics: Mapped[List["OcsfMetric"]] = relationship(
        "OcsfMetric",
        secondary="ocsf_cvss_metrics",
        back_populates="cvsses",
    )

    def __repr__(self) -> str:
        return f"<OcsfCvss(id={self.id})>"