"""Generated object model: package.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .fingerprint import OcsfFingerprint
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfPackage(OcsfObject):
    """Software Package.

    The Software Package object describes details about a software package.

    Inheritance chain: package -> object
    """
    __tablename__ = "ocsf_package"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "package"}

    # Attributes
    architecture: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Architecture is a shorthand name describing the type of computer hardware the packaged software is meant to run on.",
        nullable=True,
    )
    cpe_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The Common Platform Enumeration (CPE) name as described by (<a target='_blank' href='https://nvd.nist.gov/products/cpe'>NIST</a>) For example: <code>cpe:/a:apple:safari:16.2</code>.",
        nullable=True,
    )
    epoch: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The software package epoch. Epoch is a way to define weighted dependencies based on version numbers.",
        nullable=True,
    )
    hash_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_fingerprint.id", ondelete="SET NULL"),
        comment="Cryptographic hash to identify the binary instance of a software component. This can include any component such file, package, or library.",
        nullable=True,
    )
    license: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The software license applied to this package.",
        nullable=True,
    )
    license_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The URL pointing to the license applied on package or software. This is typically a <code>LICENSE.md</code> file within a repository.",
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        Text,
        comment="The software package name.",
        nullable=False,
    )
    package_manager: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The software packager manager utilized to manage a package on a system, e.g. npm, yum, dpkg etc.",
        nullable=True,
    )
    package_manager_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The URL of the package or library at the package manager, or the specific URL or URI of an internal package manager link such as <code>AWS CodeArtifact</code> or <code>Artifactory</code>.",
        nullable=True,
    )
    purl: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="A purl is a URL string used to identify and locate a software package in a mostly universal and uniform way across programming languages, package managers, packaging conventions, tools, APIs and databases.",
        nullable=True,
    )
    release: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="Release is the number of times a version of the software has been packaged.",
        nullable=True,
    )
    src_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The link to the specific library or package such as within <code>GitHub</code>, this is different from the link to the package manager where the library or package is hosted.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type of software package, normalized to the caption of the <code>type_id</code> value. In the case of 'Other', it is defined by the source.",
        nullable=True,
    )
    type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The type of software package.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="A unique identifier for the package or library reported by the source tool. E.g., the <code>libId</code> within the <code>sbom</code> field of an OX Security Issue or the SPDX...",
        nullable=True,
    )
    vendor_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the vendor who published the software package.",
        nullable=True,
    )
    version: Mapped[str] = mapped_column(
        Text,
        comment="The software package version.",
        nullable=False,
    )

    # Relationships
    hash: Mapped[Optional["OcsfFingerprint"]] = relationship(
        "OcsfFingerprint",
        foreign_keys=[hash_id],
        back_populates="packages",
    )

    def __repr__(self) -> str:
        return f"<OcsfPackage(id={self.id})>"