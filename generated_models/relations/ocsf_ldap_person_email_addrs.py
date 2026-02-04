"""Generated primitive_array model: ocsf_ldap_person_email_addrs.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    ForeignKey, String, Text, Integer, BigInteger, Float,
    Boolean, DateTime, LargeBinary, Uuid, Table, Column, func,
)
from sqlalchemy.dialects.postgresql import INET, CIDR
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfOcsfLdapPersonEmailAddrs(OcsfBase):
    """Association table for ldap_person.email_addrs.

    Stores primitive array values in a normalized one-to-many relationship.
    """
    __tablename__ = "ocsf_ldap_person_email_addrs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ldap_person_id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_ldap_person.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value: Mapped[Optional[str]] = mapped_column(
        String(254),
        nullable=True,
        comment="Values for ldap_person.email_addrs",
    )
    position: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Order in the array",
    )

    # Relationship back to parent
    ldap_person: Mapped["OcsfLdapPerson"] = relationship(
        "OcsfLdapPerson",
        back_populates="email_addrs",
    )

    def __repr__(self) -> str:
        return f"<OcsfOcsfLdapPersonEmailAddrs(id={self.id}, value={self.value})>"