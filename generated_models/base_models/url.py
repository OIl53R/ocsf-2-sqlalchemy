"""Generated object model: url.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfUrl(OcsfObject):
    """Uniform Resource Locator.

    The Uniform Resource Locator (URL) object describes the characteristics
    of a URL.

    Inheritance chain: url -> object
    """
    __tablename__ = "ocsf_url"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "url"}

    # Attributes
    domain: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The domain portion of the URL. For example: <code>example.com</code> in <code>https://sub.example.com</code>.",
        nullable=True,
    )
    hostname: Mapped[Optional[str]] = mapped_column(
        String(253),
        comment="The URL host as extracted from the URL. For example: <code>www.example.com</code> from <code>www.example.com/download/trouble</code>.",
        nullable=True,
    )
    path: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The URL path as extracted from the URL. For example: <code>/download/trouble</code> from <code>www.example.com/download/trouble</code>.",
        nullable=True,
    )
    port: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The URL port. For example: <code>80</code>.",
        nullable=True,
    )
    query_string: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The query portion of the URL. For example: the query portion of the URL <code>http://www.example.com/search?q=bad&sort=date</code> is <code>q=bad&sort=date</code>.",
        nullable=True,
    )
    resource_type: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The context in which a resource was retrieved in a web request.",
        nullable=True,
    )
    scheme: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The scheme portion of the URL. For example: <code>http</code>, <code>https</code>, <code>ftp</code>, or <code>sftp</code>.",
        nullable=True,
    )
    subdomain: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The subdomain portion of the URL. For example: <code>sub</code> in <code>https://sub.example.com</code> or <code>sub2.sub1</code> in <code>https://sub2.sub1.example.com</code>.",
        nullable=True,
    )
    url_string: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The URL string. See RFC 1738. For example: <code>http://www.example.com/download/trouble.exe</code>. Note: The URL path should not populate the URL string.",
        nullable=True,
    )


    def __repr__(self) -> str:
        return f"<OcsfUrl(id={self.id})>"