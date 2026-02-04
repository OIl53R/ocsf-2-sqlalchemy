"""Generated object model: timespan.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfTimespan(OcsfObject):
    """Time Span.

    The Time Span object represents different time period durations. If a
    timespan is fractional, i.e. crosses one period, e.g. a week and 3 days,
    more than one may be populated since each member is of integral type. In
    that case <code>type_id</code> if present should be set to
    <code>Other.</code><P>A timespan may also be defined by its time
    interval boundaries, <code>start_time</code> and <code>end_time</code>.

    Inheritance chain: timespan -> object
    """
    __tablename__ = "ocsf_timespan"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "timespan"}

    # Attributes
    duration: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The duration of the time span in milliseconds.",
        nullable=True,
    )
    duration_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in days.",
        nullable=True,
    )
    duration_hours: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in hours.",
        nullable=True,
    )
    duration_mins: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in minutes.",
        nullable=True,
    )
    duration_months: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in months.",
        nullable=True,
    )
    duration_secs: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in seconds.",
        nullable=True,
    )
    duration_weeks: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in weeks.",
        nullable=True,
    )
    duration_years: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The duration of the time span in years.",
        nullable=True,
    )
    end_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The end time or conclusion of the timespan's interval.",
        nullable=True,
    )
    start_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The start time or beginning of the timespan's interval.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type of time span duration the object represents.",
        nullable=True,
    )
    type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized identifier for the time span duration type.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfTimespan(id={self.id})>"