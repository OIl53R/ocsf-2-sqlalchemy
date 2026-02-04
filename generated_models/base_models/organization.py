"""Generated object model: organization.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from typing import Optional, List
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfOrganization(OcsfEntity):
    """Organization.

    The Organization object describes characteristics of an organization or
    company and its division if any. Additionally, it also describes cloud
    and Software-as-a-Service (SaaS) logical hierarchies such as AWS
    Organizations, Google Cloud Organizations, Oracle Cloud Tenancies, and
    similar constructs.

    Inheritance chain: organization -> _entity -> object
    """
    __tablename__ = "ocsf_organization"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "organization"}

    # Attributes
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the organization, Oracle Cloud Tenancy, Google Cloud Organization, or AWS Organization. For example, <code> Widget, Inc. </code> or the <code> AWS Organization name </code>.",
        nullable=True,
    )
    ou_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of an organizational unit, Google Cloud Folder, or AWS Org Unit. For example, the <code> GCP Project Name </code>, or <code> Dev_Prod_OU </code>.",
        nullable=True,
    )
    ou_uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of an organizational unit, Google Cloud Folder, or AWS Org Unit. For example, an  <code> Oracle Cloud Tenancy ID </code>, <code> AWS OU ID </code>, or <code> GCP Folder ID </code>.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the organization, Oracle Cloud Tenancy, Google Cloud Organization, or AWS Organization. For example, an <code> AWS Org ID </code> or <code> Oracle Cloud Domain ID </code>.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfOrganization(id={self.id})>"