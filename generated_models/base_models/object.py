"""Generated object model: object.

Auto-generated from OCSF schema version 1.8.0-dev.
DO NOT EDIT MANUALLY.
"""

from ..base import OcsfBase, OcsfTimestampMixin
from typing import Optional, List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class OcsfObject(OcsfBase, OcsfTimestampMixin):
    """Object.

    An unordered collection of attributes. It defines a set of attributes
    available in all objects. It can be also used as a generic object to log
    objects that are not otherwise defined by the schema.
    """
    __tablename__ = "ocsf_object"

    id: Mapped[int] = mapped_column(primary_key=True)
    _type: Mapped[str] = mapped_column(String(100), nullable=False)
    __mapper_args__ = {
        "polymorphic_on": "_type",
        "polymorphic_identity": "object",
    }



    def __repr__(self) -> str:
        return f"<OcsfObject(id={self.id})>"