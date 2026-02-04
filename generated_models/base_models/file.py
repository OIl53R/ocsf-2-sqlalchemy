"""Generated object model: file.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from .digital_signature import OcsfDigitalSignature
from .encryption_details import OcsfEncryptionDetails
from .fingerprint import OcsfFingerprint
from .key_value_object import OcsfKeyValueObject
from .object import OcsfObject
from .product import OcsfProduct
from .url import OcsfUrl
from .user import OcsfUser
from typing import Optional, List
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfFile(OcsfEntity):
    """File.

    The File object represents the metadata associated with a file stored in
    a computer system. It encompasses information about the file itself,
    including its attributes, properties, and organizational details.

    Inheritance chain: file -> _entity -> object
    """
    __tablename__ = "ocsf_file"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "file"}

    # Attributes
    accessed_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The time when the file was last accessed.",
        nullable=True,
    )
    accessor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_user.id", ondelete="SET NULL"),
        comment="The name of the user who last accessed the object.",
        nullable=True,
    )
    attributes: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The bitmask value that represents the file attributes.",
        nullable=True,
    )
    company_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the company that published the file. For example: <code>Microsoft Corporation</code>.",
        nullable=True,
    )
    confidentiality: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The file content confidentiality, normalized to the confidentiality_id value. In the case of 'Other', it is defined by the event source.",
        nullable=True,
    )
    confidentiality_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized identifier of the file content confidentiality indicator.",
        nullable=True,
    )
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The time when the file was created.",
        nullable=True,
    )
    creator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_user.id", ondelete="SET NULL"),
        comment="The user that created the file.",
        nullable=True,
    )
    desc: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The description of the file, as returned by file system. For example: the description as returned by the Unix file command or the Windows file type.",
        nullable=True,
    )
    drive_type: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The drive type, normalized to the caption of the <code>drive_type_id</code> value. In the case of <code>Other</code>, it is defined by the source.",
        nullable=True,
    )
    drive_type_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="Identifies the type of a disk drive, i.e. fixed, removable, etc.",
        nullable=True,
    )
    encryption_details_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_encryption_details.id", ondelete="SET NULL"),
        comment="The encryption details of the file. Should be populated if the file is encrypted.",
        nullable=True,
    )
    ext: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The extension of the file, excluding the leading dot. For example: <code>exe</code> from <code>svchost.exe</code>, or <code>gz</code> from <code>export.tar.gz</code>.",
        nullable=True,
    )
    internal_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the file as identified within the file itself. This contrasts with the name by which the file is known on disk. Where available, the internal name is widely used by security...",
        nullable=True,
    )
    is_deleted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="Indicates if the file was deleted from the filesystem.",
        nullable=True,
    )
    is_encrypted: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="Indicates if the file is encrypted.",
        nullable=True,
    )
    is_public: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="Indicates if the file is publicly accessible. For example in an object's public access in AWS S3",
        nullable=True,
    )
    is_readonly: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="Indicates that the file cannot be modified.",
        nullable=True,
    )
    is_system: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="The indication of whether the object is part of the operating system.",
        nullable=True,
    )
    mime_type: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The Multipurpose Internet Mail Extensions (MIME) type of the file, if applicable.",
        nullable=True,
    )
    modified_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The time when the file was last modified.",
        nullable=True,
    )
    modifier_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_user.id", ondelete="SET NULL"),
        comment="The user that last modified the file.",
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        Text,
        comment="The name of the file. For example: <code>svchost.exe</code>",
        nullable=False,
    )
    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_user.id", ondelete="SET NULL"),
        comment="The user that owns the file/object.",
        nullable=True,
    )
    parent_folder: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The parent folder in which the file resides. For example: <code>c:\windows\system32</code>",
        nullable=True,
    )
    path: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The full path to the file. For example: <code>c:\windows\system32\svchost.exe</code>.",
        nullable=True,
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_product.id", ondelete="SET NULL"),
        comment="The product that created or installed the file.",
        nullable=True,
    )
    security_descriptor: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The object security descriptor.",
        nullable=True,
    )
    signature_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_digital_signature.id", ondelete="SET NULL"),
        comment="The digital signature of the file.",
        nullable=True,
    )
    size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The size of data, in bytes.",
        nullable=True,
    )
    storage_class: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The storage class of the file. For example in AWS S3: <code>STANDARD, STANDARD_IA, GLACIER</code>.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The file type.",
        nullable=True,
    )
    type_id: Mapped[int] = mapped_column(
        Integer,
        comment="The file type ID. Note the distinction between a <code>Regular File</code> and an <code>Executable File</code>. If the distinction is not known, or not indicated by the log, use <code>Regular...",
        nullable=False,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the file as defined by the storage system, such the file system file ID.",
        nullable=True,
    )
    uri: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The file URI, such as those reporting by static analysis tools. E.g., <code>file:///C:/dev/sarif/sarif-tutorials/samples/Introduction/simple-example.js</code>",
        nullable=True,
    )
    url_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_url.id", ondelete="SET NULL"),
        comment="The URL of the file, when applicable.",
        nullable=True,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The file version. For example: <code>8.0.7601.17514</code>.",
        nullable=True,
    )
    volume: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The volume on the storage device where the file is located.",
        nullable=True,
    )
    xattributes_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="SET NULL"),
        comment="An unordered collection of zero or more name/value pairs where each pair represents a file or folder extended attribute.</p>For example: Windows alternate data stream attributes (ADS stream name,...",
        nullable=True,
    )

    # Relationships
    accessor: Mapped[Optional["OcsfUser"]] = relationship(
        "OcsfUser",
        foreign_keys=[accessor_id],
        back_populates="files",
    )
    creator: Mapped[Optional["OcsfUser"]] = relationship(
        "OcsfUser",
        foreign_keys=[creator_id],
        back_populates="files",
    )
    encryption_details: Mapped[Optional["OcsfEncryptionDetails"]] = relationship(
        "OcsfEncryptionDetails",
        foreign_keys=[encryption_details_id],
        back_populates="files",
    )
    hashes: Mapped[List["OcsfFingerprint"]] = relationship(
        "OcsfFingerprint",
        secondary="ocsf_file_hashes",
        back_populates="files",
    )
    modifier: Mapped[Optional["OcsfUser"]] = relationship(
        "OcsfUser",
        foreign_keys=[modifier_id],
        back_populates="files",
    )
    owner: Mapped[Optional["OcsfUser"]] = relationship(
        "OcsfUser",
        foreign_keys=[owner_id],
        back_populates="files",
    )
    product: Mapped[Optional["OcsfProduct"]] = relationship(
        "OcsfProduct",
        foreign_keys=[product_id],
        back_populates="files",
    )
    signature: Mapped[Optional["OcsfDigitalSignature"]] = relationship(
        "OcsfDigitalSignature",
        foreign_keys=[signature_id],
        back_populates="files",
    )
    signatures: Mapped[List["OcsfDigitalSignature"]] = relationship(
        "OcsfDigitalSignature",
        secondary="ocsf_file_signatures",
        back_populates="files",
    )
    tags: Mapped[List["OcsfKeyValueObject"]] = relationship(
        "OcsfKeyValueObject",
        secondary="ocsf_file_tags",
        back_populates="files",
    )
    url: Mapped[Optional["OcsfUrl"]] = relationship(
        "OcsfUrl",
        foreign_keys=[url_id],
        back_populates="files",
    )
    xattributes: Mapped[Optional["OcsfObject"]] = relationship(
        "OcsfObject",
        foreign_keys=[xattributes_id],
        back_populates="files",
    )

    def __repr__(self) -> str:
        return f"<OcsfFile(id={self.id})>"