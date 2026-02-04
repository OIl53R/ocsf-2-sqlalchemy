"""Generated object model: programmatic_credential.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfProgrammaticCredential(OcsfObject):
    """Programmatic Credential.

    The Programmatic Credential object describes service-specific
    credentials used for direct API access and system integration. These
    credentials are typically issued by individual services or platforms for
    accessing their APIs and resources, focusing on credential lifecycle
    management and usage tracking. Examples include API keys, service
    account keys, client certificates, and vendor-specific access tokens.

    Inheritance chain: programmatic_credential -> object
    """
    __tablename__ = "ocsf_programmatic_credential"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "programmatic_credential"}

    # Attributes
    last_used_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp when this programmatic credential was last used for authentication or API access. This helps track credential usage patterns, identify dormant credentials that may pose security...",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type or category of programmatic credential, normalized to the caption of the type_id value. In the case of 'Other', it is defined by the event source. Examples include 'API Key', 'Service...",
        nullable=True,
    )
    uid: Mapped[str] = mapped_column(
        Text,
        comment="The unique identifier of the programmatic credential. This could be an API key ID, service account key ID, access token identifier, certificate serial number, or other unique identifier that...",
        nullable=False,
    )


    def __repr__(self) -> str:
        return f"<OcsfProgrammaticCredential(id={self.id})>"