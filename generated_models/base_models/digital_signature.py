"""Generated object model: digital_signature.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from ..events.certificate import OcsfCertificate
from .fingerprint import OcsfFingerprint
from typing import Optional, List
from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfDigitalSignature(OcsfObject):
    """Digital Signature.

    The Digital Signature object contains information about the
    cryptographic mechanism used to verify the authenticity, integrity, and
    origin of the file or application.

    Inheritance chain: digital_signature -> object
    """
    __tablename__ = "ocsf_digital_signature"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "digital_signature"}

    # Attributes
    algorithm: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The digital signature algorithm used to create the signature, normalized to the caption of 'algorithm_id'. In the case of 'Other', it is defined by the event source.",
        nullable=True,
    )
    algorithm_id: Mapped[int] = mapped_column(
        Integer,
        comment="The identifier of the normalized digital signature algorithm.",
        nullable=False,
    )
    certificate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_certificate.id", ondelete="SET NULL"),
        comment="The certificate object containing information about the digital certificate.",
        nullable=True,
    )
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The time when the digital signature was created.",
        nullable=True,
    )
    developer_uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The developer ID on the certificate that signed the file.",
        nullable=True,
    )
    digest_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_fingerprint.id", ondelete="SET NULL"),
        comment="The message digest attribute contains the fixed length message hash representation and the corresponding hashing algorithm information.",
        nullable=True,
    )
    state: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The digital signature state defines the signature state, normalized to the caption of 'state_id'. In the case of 'Other', it is defined by the event source.",
        nullable=True,
    )
    state_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized identifier of the signature state.",
        nullable=True,
    )

    # Relationships
    certificate: Mapped[Optional["OcsfCertificate"]] = relationship(
        "OcsfCertificate",
        foreign_keys=[certificate_id],
        back_populates="digital_signatures",
    )
    digest: Mapped[Optional["OcsfFingerprint"]] = relationship(
        "OcsfFingerprint",
        foreign_keys=[digest_id],
        back_populates="digital_signatures",
    )

    def __repr__(self) -> str:
        return f"<OcsfDigitalSignature(id={self.id})>"