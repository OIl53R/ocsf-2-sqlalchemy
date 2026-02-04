"""Generated object model: kb_article.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from .object import OcsfObject
from .os import OcsfOs
from .product import OcsfProduct
from .timespan import OcsfTimespan
from typing import Optional, List
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfKbArticle(OcsfObject):
    """KB Article.

    The KB Article object contains metadata that describes the patch or
    update.

    Inheritance chain: kb_article -> object
    """
    __tablename__ = "ocsf_kb_article"

    # Joined table inheritance from object
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_object.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "kb_article"}

    # Attributes
    avg_timespan_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_timespan.id", ondelete="SET NULL"),
        comment="The average time to patch.",
        nullable=True,
    )
    bulletin: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The kb article bulletin identifier.",
        nullable=True,
    )
    classification: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The vendors classification of the kb article.",
        nullable=True,
    )
    created_time: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The date the kb article was released by the vendor.",
        nullable=True,
    )
    install_state: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The install state of the kb article.",
        nullable=True,
    )
    install_state_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        comment="The normalized install state ID of the kb article.",
        nullable=True,
    )
    is_superseded: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        comment="The kb article has been replaced by another.",
        nullable=True,
    )
    os_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_os.id", ondelete="SET NULL"),
        comment="The operating system the kb article applies.",
        nullable=True,
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_product.id", ondelete="SET NULL"),
        comment="The product details the kb article applies.",
        nullable=True,
    )
    severity: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The severity of the kb article.",
        nullable=True,
    )
    size: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        comment="The size in bytes for the kb article.",
        nullable=True,
    )
    src_url: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The kb article link from the source vendor.",
        nullable=True,
    )
    title: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The title of the kb article.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier for the kb article.",
        nullable=True,
    )

    # Relationships
    avg_timespan: Mapped[Optional["OcsfTimespan"]] = relationship(
        "OcsfTimespan",
        foreign_keys=[avg_timespan_id],
        back_populates="kb_articles",
    )
    os: Mapped[Optional["OcsfOs"]] = relationship(
        "OcsfOs",
        foreign_keys=[os_id],
        back_populates="kb_articles",
    )
    product: Mapped[Optional["OcsfProduct"]] = relationship(
        "OcsfProduct",
        foreign_keys=[product_id],
        back_populates="kb_articles",
    )

    def __repr__(self) -> str:
        return f"<OcsfKbArticle(id={self.id})>"