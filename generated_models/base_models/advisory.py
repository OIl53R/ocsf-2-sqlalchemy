"""Generated object model: advisory.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .cve import OcsfCve
from .cwe import OcsfCwe
from .os import OcsfOs
from .product import OcsfProduct
from .timespan import OcsfTimespan
from typing import Optional, List
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfAdvisory(OcsfObject):
    """Advisory.

    The Advisory object represents publicly disclosed cybersecurity
    vulnerabilities defined in a Security advisory. e.g. <code> Microsoft KB
    Article</code>, <code>Apple Security Advisory</code>, or a <code>GitHub
    Security Advisory (GHSA)</code>

    Inheritance chain: advisory -> object
    """
    __tablename__ = "ocsf_advisory"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "advisory"}

    # Attributes
    avg_timespan_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_timespan.id", ondelete="SET NULL"),
        comment="The average time to patch.",
        nullable=True,
    )
    bulletin: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The Advisory bulletin identifier.",
        nullable=True,
    )
    classification: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The vendors classification of the Advisory.",
        nullable=True,
    )
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The time when the Advisory record was created.",
        nullable=True,
    )
    desc: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="A brief description of the Advisory Record.",
        nullable=True,
    )
    install_state: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The install state of the Advisory.",
        nullable=True,
    )
    install_state_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized install state ID of the Advisory.",
        nullable=True,
    )
    is_superseded: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="The Advisory has been replaced by another.",
        nullable=True,
    )
    modified_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The time when the Advisory record was last updated.",
        nullable=True,
    )
    os_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_os.id", ondelete="SET NULL"),
        comment="The operating system the Advisory applies to.",
        nullable=True,
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_product.id", ondelete="SET NULL"),
        comment="The product where the vulnerability was discovered.",
        nullable=True,
    )
    size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The size in bytes for the Advisory. Usually populated for a KB Article patch.",
        nullable=True,
    )
    src_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The Advisory link from the source vendor.",
        nullable=True,
    )
    title: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="A title or a brief phrase summarizing the Advisory.",
        nullable=True,
    )
    uid: Mapped[str] = mapped_column(
        Text,
        comment="The unique identifier assigned to the advisory or disclosed vulnerability, e.g, <code>GHSA-5mrr-rgp6-x4gr</code>.",
        nullable=False,
    )

    # Relationships
    avg_timespan: Mapped[Optional["OcsfTimespan"]] = relationship(
        "OcsfTimespan",
        foreign_keys=[avg_timespan_id],
        back_populates="advisories",
    )
    os: Mapped[Optional["OcsfOs"]] = relationship(
        "OcsfOs",
        foreign_keys=[os_id],
        back_populates="advisories",
    )
    product: Mapped[Optional["OcsfProduct"]] = relationship(
        "OcsfProduct",
        foreign_keys=[product_id],
        back_populates="advisories",
    )
    related_cves: Mapped[List["OcsfCve"]] = relationship(
        "OcsfCve",
        secondary="ocsf_advisory_related_cves",
        back_populates="advisories",
    )
    related_cwes: Mapped[List["OcsfCwe"]] = relationship(
        "OcsfCwe",
        secondary="ocsf_advisory_related_cwes",
        back_populates="advisories",
    )

    def __repr__(self) -> str:
        return f"<OcsfAdvisory(id={self.id})>"