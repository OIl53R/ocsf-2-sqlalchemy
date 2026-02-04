"""Generated object model: encryption_details.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfEncryptionDetails(OcsfObject):
    """Encryption Details.

    Details about the encryption methodology utilized.

    Inheritance chain: encryption_details -> object
    """
    __tablename__ = "ocsf_encryption_details"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "encryption_details"}

    # Attributes
    algorithm: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The encryption algorithm used, normalized to the caption of 'algorithm_id",
        nullable=True,
    )
    algorithm_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The encryption algorithm used.",
        nullable=True,
    )
    key_length: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The length of the encryption key used.",
        nullable=True,
    )
    key_uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the key used for encryption. For example, AWS KMS Key ARN.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type of the encryption used.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfEncryptionDetails(id={self.id})>"