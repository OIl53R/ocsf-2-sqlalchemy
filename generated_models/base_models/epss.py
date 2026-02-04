"""Generated object model: epss.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import BigInteger, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfEpss(OcsfObject):
    """EPSS.

    The Exploit Prediction Scoring System (EPSS) object describes the
    estimated probability a vulnerability will be exploited. EPSS is a
    community-driven effort to combine descriptive information about
    vulnerabilities (CVEs) with evidence of actual exploitation in-the-wild.
    (<a target='_blank' href='https://www.first.org/epss/'>EPSS</a>).

    Inheritance chain: epss -> object
    """
    __tablename__ = "ocsf_epss"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "epss"}

    # Attributes
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp indicating when the EPSS score was calculated.",
        nullable=True,
    )
    percentile: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="The EPSS score's percentile representing relative importance and ranking of the score in the larger EPSS dataset.",
        nullable=True,
    )
    score: Mapped[str] = mapped_column(
        Text,
        comment="The EPSS score representing the probability [0-1] of exploitation in the wild in the next 30 days (following score publication).",
        nullable=False,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The version of the EPSS model used to calculate the score.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfEpss(id={self.id})>"