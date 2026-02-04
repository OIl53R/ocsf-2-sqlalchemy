"""Generated object model: cve.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .cvss import OcsfCvss
from .cwe import OcsfCwe
from .epss import OcsfEpss
from .product import OcsfProduct
from typing import Optional, List
from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfCve(OcsfObject):
    """CVE.

    The Common Vulnerabilities and Exposures (CVE) object represents
    publicly disclosed cybersecurity vulnerabilities defined in CVE Program
    catalog (<a target='_blank' href='https://cve.mitre.org/'>CVE</a>).
    There is one CVE Record for each vulnerability in the catalog.

    Inheritance chain: cve -> object
    """
    __tablename__ = "ocsf_cve"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "cve"}

    # Attributes
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The Record Creation Date identifies when the CVE ID was issued to a CVE Numbering Authority (CNA) or the CVE Record was published on the CVE List. Note that the Record Creation Date does not...",
        nullable=True,
    )
    cwe_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_cwe.id", ondelete="SET NULL"),
        comment="The CWE object represents a weakness in a software system that can be exploited by a threat actor to perform an attack. The CWE object is based on the <a target='_blank'...",
        nullable=True,
    )
    cwe_uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The <a target='_blank' href='https://cwe.mitre.org/'>Common Weakness Enumeration (CWE)</a> unique identifier. For example: <code>CWE-787</code>.",
        nullable=True,
    )
    cwe_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Common Weakness Enumeration (CWE) definition URL. For example: <code>https://cwe.mitre.org/data/definitions/787.html</code>.",
        nullable=True,
    )
    desc: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="A brief description of the CVE Record.",
        nullable=True,
    )
    epss_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_epss.id", ondelete="SET NULL"),
        comment="The Exploit Prediction Scoring System (EPSS) object describes the estimated probability a vulnerability will be exploited. EPSS is a community-driven effort to combine descriptive information...",
        nullable=True,
    )
    modified_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The Record Modified Date identifies when the CVE record was last updated.",
        nullable=True,
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_product.id", ondelete="SET NULL"),
        comment="The product where the vulnerability was discovered.",
        nullable=True,
    )
    title: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="A title or a brief phrase summarizing the CVE record.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="<p>The vulnerability type as selected from a large dropdown menu during CVE refinement.</p>Most frequently used vulnerability types are: <code>DoS</code>, <code>Code Execution</code>,...",
        nullable=True,
    )
    uid: Mapped[str] = mapped_column(
        Text,
        comment="The Common Vulnerabilities and Exposures unique number assigned to a specific computer vulnerability. A CVE Identifier begins with 4 digits representing the year followed by a sequence of digits...",
        nullable=False,
    )

    # Relationships
    cvss: Mapped[List["OcsfCvss"]] = relationship(
        "OcsfCvss",
        secondary="ocsf_cve_cvss",
        back_populates="cves",
    )
    cwe: Mapped[Optional["OcsfCwe"]] = relationship(
        "OcsfCwe",
        foreign_keys=[cwe_id],
        back_populates="cves",
    )
    epss: Mapped[Optional["OcsfEpss"]] = relationship(
        "OcsfEpss",
        foreign_keys=[epss_id],
        back_populates="cves",
    )
    product: Mapped[Optional["OcsfProduct"]] = relationship(
        "OcsfProduct",
        foreign_keys=[product_id],
        back_populates="cves",
    )
    related_cwes: Mapped[List["OcsfCwe"]] = relationship(
        "OcsfCwe",
        secondary="ocsf_cve_related_cwes",
        back_populates="cves",
    )

    def __repr__(self) -> str:
        return f"<OcsfCve(id={self.id})>"