"""Generated object model: user.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from .account import OcsfAccount
from .group import OcsfGroup
from .ldap_person import OcsfLdapPerson
from .organization import OcsfOrganization
from .programmatic_credential import OcsfProgrammaticCredential
from typing import Optional, List
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfUser(OcsfEntity):
    """User.

    The User object describes the characteristics of a user/person or a
    security principal.

    Inheritance chain: user -> _entity -> object
    """
    __tablename__ = "ocsf_user"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "user"}

    # Attributes
    account_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_account.id", ondelete="SET NULL"),
        comment="The user's account or the account associated with the user.",
        nullable=True,
    )
    credential_uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the user's credential. For example, AWS Access Key ID.",
        nullable=True,
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The display name of the user, as reported by the product.",
        nullable=True,
    )
    domain: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The domain where the user is defined. For example: the LDAP or Active Directory domain.",
        nullable=True,
    )
    email_addr: Mapped[Optional[str]] = mapped_column(
        String(254),
        comment="The user's primary email address.",
        nullable=True,
    )
    forward_addr: Mapped[Optional[str]] = mapped_column(
        String(254),
        comment="The user's forwarding email address.",
        nullable=True,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The full name of the user, as reported by the product.",
        nullable=True,
    )
    has_mfa: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="The user has a multi-factor or secondary-factor device assigned.",
        nullable=True,
    )
    ldap_person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_ldap_person.id", ondelete="SET NULL"),
        comment="The additional LDAP attributes that describe a person.",
        nullable=True,
    )
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The username. For example, <code>janedoe1</code>.",
        nullable=True,
    )
    org_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_organization.id", ondelete="SET NULL"),
        comment="Organization and org unit related to the user.",
        nullable=True,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The telephone number of the user.",
        nullable=True,
    )
    risk_level: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The risk level, normalized to the caption of the risk_level_id value.",
        nullable=True,
    )
    risk_level_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized risk level id.",
        nullable=True,
    )
    risk_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The risk score as reported by the event source.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type of the user. For example, System, AWS IAM User, etc.",
        nullable=True,
    )
    type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The account type identifier.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique user identifier. For example, the Windows user SID, ActiveDirectory DN or AWS user ARN.",
        nullable=True,
    )
    uid_alt: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The alternate user identifier. For example, the Active Directory user GUID or AWS user Principal ID.",
        nullable=True,
    )

    # Relationships
    account: Mapped[Optional["OcsfAccount"]] = relationship(
        "OcsfAccount",
        foreign_keys=[account_id],
        back_populates="users",
    )
    groups: Mapped[List["OcsfGroup"]] = relationship(
        "OcsfGroup",
        secondary="ocsf_user_groups",
        back_populates="users",
    )
    ldap_person: Mapped[Optional["OcsfLdapPerson"]] = relationship(
        "OcsfLdapPerson",
        foreign_keys=[ldap_person_id],
        back_populates="users",
    )
    org: Mapped[Optional["OcsfOrganization"]] = relationship(
        "OcsfOrganization",
        foreign_keys=[org_id],
        back_populates="users",
    )
    programmatic_credentials: Mapped[List["OcsfProgrammaticCredential"]] = relationship(
        "OcsfProgrammaticCredential",
        secondary="ocsf_user_programmatic_credentials",
        back_populates="users",
    )

    def __repr__(self) -> str:
        return f"<OcsfUser(id={self.id})>"