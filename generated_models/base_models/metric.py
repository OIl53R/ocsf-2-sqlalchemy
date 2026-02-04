"""Generated object model: metric.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfMetric(OcsfObject):
    """Metric.

    The Metric object defines a simple name/value pair entity for a metric.

    Inheritance chain: metric -> object
    """
    __tablename__ = "ocsf_metric"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "metric"}

    # Attributes
    name: Mapped[str] = mapped_column(
        Text,
        comment="The name of the metric.",
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        Text,
        comment="The value of the metric.",
        nullable=False,
    )


    def __repr__(self) -> str:
        return f"<OcsfMetric(id={self.id})>"