"""Generated object model: account.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from .key_value_object import OcsfKeyValueObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfAccount(OcsfEntity):
    """Account.

    The Account object contains details about the account that initiated or
    performed a specific activity within a system or application.
    Additionally, the Account object refers to logical Cloud and Software-
    as-a-Service (SaaS) based containers such as AWS Accounts, Azure
    Subscriptions, Oracle Cloud Compartments, Google Cloud Projects, and
    otherwise.

    Inheritance chain: account -> _entity -> object
    """
    __tablename__ = "ocsf_account"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "account"}

    # Attributes
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the account (e.g. <code> GCP Project name </code>, <code> Linux Account name </code> or <code> AWS Account name</code>).",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The account type, normalized to the caption of 'account_type_id'. In the case of 'Other', it is defined by the event source.",
        nullable=True,
    )
    type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized account type identifier.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the account (e.g. <code> AWS Account ID </code>, <code> OCID </code>, <code> GCP Project ID </code>, <code> Azure Subscription ID </code>, <code> Google Workspace Customer...",
        nullable=True,
    )

    # Relationships
    tags: Mapped[List["OcsfKeyValueObject"]] = relationship(
        "OcsfKeyValueObject",
        secondary="ocsf_account_tags",
        back_populates="accounts",
    )

    def __repr__(self) -> str:
        return f"<OcsfAccount(id={self.id})>"