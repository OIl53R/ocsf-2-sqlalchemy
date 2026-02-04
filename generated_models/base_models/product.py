"""Generated object model: product.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from ._entity import OcsfEntity
from .feature import OcsfFeature
from typing import Optional, List
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfProduct(OcsfEntity):
    """Product.

    The Product object describes characteristics of a software product.

    Inheritance chain: product -> _entity -> object
    """
    __tablename__ = "ocsf_product"

    # Joined table inheritance from _entity
    id: Mapped[int] = mapped_column(
        ForeignKey("ocsf_entity.id", ondelete="CASCADE"),
        primary_key=True,
    )
    __mapper_args__ = {"polymorphic_identity": "product"}

    # Attributes
    cpe_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The Common Platform Enumeration (CPE) name as described by (<a target='_blank' href='https://nvd.nist.gov/products/cpe'>NIST</a>) For example: <code>cpe:/a:apple:safari:16.2</code>.",
        nullable=True,
    )
    feature_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ocsf_feature.id", ondelete="SET NULL"),
        comment="The feature that reported the event.",
        nullable=True,
    )
    lang: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The two letter lower case language codes, as defined by <a target='_blank' href='https://en.wikipedia.org/wiki/ISO_639-1'>ISO 639-1</a>. For example: <code>en</code> (English), <code>de</code>...",
        nullable=True,
    )
    name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the product.",
        nullable=True,
    )
    path: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The installation path of the product.",
        nullable=True,
    )
    uid: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The unique identifier of the product.",
        nullable=True,
    )
    url_string: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The URL pointing towards the product.",
        nullable=True,
    )
    vendor_name: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The name of the vendor of the product.",
        nullable=True,
    )
    version: Mapped[Optional[str]] = mapped_column(
        Text,
        comment="The version of the product, as defined by the event source. For example: <code>2013.1.3-beta</code>.",
        nullable=True,
    )

    # Relationships
    feature: Mapped[Optional["OcsfFeature"]] = relationship(
        "OcsfFeature",
        foreign_keys=[feature_id],
        back_populates="products",
    )

    def __repr__(self) -> str:
        return f"<OcsfProduct(id={self.id})>"