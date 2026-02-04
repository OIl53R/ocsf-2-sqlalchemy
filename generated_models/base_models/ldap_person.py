"""Generated object model: ldap_person.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from ..events.location import OcsfLocation
from .key_value_object import OcsfKeyValueObject
from .user import OcsfUser
from typing import Optional, List
from sqlalchemy import BigInteger, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfLdapPerson(OcsfObject):
    """LDAP Person.

    The additional LDAP attributes that describe a person.

    Inheritance chain: ldap_person -> object
    """
    __tablename__ = "ocsf_ldap_person"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "ldap_person"}

    # Attributes
    cost_center: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The cost center associated with the user.",
        nullable=True,
    )
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp when the user was created.",
        nullable=True,
    )
    deleted_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp when the user was deleted. In Active Directory (AD), when a user is deleted they are moved to a temporary container and then removed after 30 days. So, this field can be populated...",
        nullable=True,
    )
    display_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The display name of the LDAP person. According to RFC 2798, this is the preferred name of a person to be used when displaying entries.",
        nullable=True,
    )
    employee_uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The employee identifier assigned to the user by the organization.",
        nullable=True,
    )
    given_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The given or first name of the user.",
        nullable=True,
    )
    hire_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp when the user was or will be hired by the organization.",
        nullable=True,
    )
    job_title: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The user's job title.",
        nullable=True,
    )
    last_login_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The last time when the user logged in.",
        nullable=True,
    )
    ldap_cn: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The LDAP and X.500 <code>commonName</code> attribute, typically the full name of the person. For example, <code>John Doe</code>.",
        nullable=True,
    )
    ldap_dn: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The X.500 Distinguished Name (DN) is a structured string that uniquely identifies an entry, such as a user, in an X.500 directory service For example, <code>cn=John Doe,ou=People,dc=example,dc=com</code>.",
        nullable=True,
    )
    leave_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp when the user left or will be leaving the organization.",
        nullable=True,
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_location.id", ondelete="SET NULL"),
        comment="The geographical location associated with a user. This is typically the user's usual work location.",
        nullable=True,
    )
    manager_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_user.id", ondelete="SET NULL"),
        comment="The user's manager. This helps in understanding an org hierarchy. This should only ever be populated once in an event. I.e. there should not be a manager's manager in an event.",
        nullable=True,
    )
    modified_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The timestamp when the user entry was last modified.",
        nullable=True,
    )
    office_location: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The primary office location associated with the user. This could be any string and isn't a specific address. For example, <code>South East Virtual</code>.",
        nullable=True,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The telephone number of the user. Corresponds to the LDAP <code>Telephone-Number</code> CN.",
        nullable=True,
    )
    surname: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The last or family name for the user.",
        nullable=True,
    )

    # Relationships
    location: Mapped[Optional["OcsfLocation"]] = relationship(
        "OcsfLocation",
        foreign_keys=[location_id],
        back_populates="ldap_persons",
    )
    manager: Mapped[Optional["OcsfUser"]] = relationship(
        "OcsfUser",
        foreign_keys=[manager_id],
        back_populates="ldap_persons",
    )
    tags: Mapped[List["OcsfKeyValueObject"]] = relationship(
        "OcsfKeyValueObject",
        secondary="ocsf_ldap_person_tags",
        back_populates="ldap_persons",
    )

    def __repr__(self) -> str:
        return f"<OcsfLdapPerson(id={self.id})>"