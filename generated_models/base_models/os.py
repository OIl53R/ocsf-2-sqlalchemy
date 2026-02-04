"""Generated object model: os.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfOs(OcsfObject):
    """Operating System (OS).

    The Operating System (OS) object describes characteristics of an OS,
    such as Linux or Windows.

    Inheritance chain: os -> object
    """
    __tablename__ = "ocsf_os"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "os"}

    # Attributes
    build: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The operating system build number.",
        nullable=True,
    )
    country: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The operating system country code, as defined by the ISO 3166-1 standard (Alpha-2 code).<p><b>Note:</b> The two letter country code should be capitalized. For example: <code>US</code> or...",
        nullable=True,
    )
    cpe_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The Common Platform Enumeration (CPE) name as described by (<a target='_blank' href='https://nvd.nist.gov/products/cpe'>NIST</a>) For example: <code>cpe:/a:apple:safari:16.2</code>.",
        nullable=True,
    )
    cpu_bits: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The cpu architecture, the number of bits used for addressing in memory. For example: <code>32</code> or <code>64</code>.",
        nullable=True,
    )
    edition: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The operating system edition. For example: <code>Professional</code>.",
        nullable=True,
    )
    kernel_release: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The kernel release of the operating system. On Unix-based systems, this is determined from the <code>uname -r</code> command output, for example \"5.15.0-122-generic\".",
        nullable=True,
    )
    lang: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The two letter lower case language codes, as defined by <a target='_blank' href='https://en.wikipedia.org/wiki/ISO_639-1'>ISO 639-1</a>. For example: <code>en</code> (English), <code>de</code>...",
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        Text,
        comment="The operating system name.",
        nullable=False,
    )
    sp_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the latest Service Pack.",
        nullable=True,
    )
    sp_ver: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The version number of the latest Service Pack.",
        nullable=True,
    )
    type_: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The type of the operating system.",
        nullable=True,
    )
    type_id: Mapped[int] = mapped_column(
        Integer,
        comment="The type identifier of the operating system.",
        nullable=False,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The version of the OS running on the device that originated the event. For example: \"Windows 10\", \"OS X 10.7\", or \"iOS 9\".",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfOs(id={self.id})>"