"""Generated object model: fingerprint.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfFingerprint(OcsfObject):
    """Fingerprint.

    The Fingerprint object provides detailed information about a digital
    fingerprint, which is a compact representation of data used to identify
    a longer piece of information, such as a public key or file content. It
    contains the algorithm and value of the fingerprint, enabling efficient
    and reliable identification of the associated data.

    Inheritance chain: fingerprint -> object
    """
    __tablename__ = "ocsf_fingerprint"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "fingerprint"}

    # Attributes
    algorithm: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The hash algorithm used to create the digital fingerprint, normalized to the caption of <code>algorithm_id</code>. In the case of <code>Other</code>, it is defined by the event source.",
        nullable=True,
    )
    algorithm_id: Mapped[int] = mapped_column(
        Integer,
        comment="The identifier of the normalized hash algorithm, which was used to create the digital fingerprint.",
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        String(128),
        comment="The digital fingerprint value.",
        nullable=False,
    )


    def __repr__(self) -> str:
        return f"<OcsfFingerprint(id={self.id})>"