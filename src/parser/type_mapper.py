"""OCSF to SQLAlchemy/PostgreSQL type mapping.

This module provides the core type translation between OCSF schema types
and SQLAlchemy column types for PostgreSQL.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class OcsfTypeCategory(Enum):
    """Categories of OCSF types for mapping decisions."""

    PRIMITIVE = "primitive"
    NETWORK = "network"
    TEMPORAL = "temporal"
    STRUCTURED = "structured"
    SPECIAL = "special"


@dataclass
class TypeMapping:
    """Represents a mapping from OCSF type to SQLAlchemy type."""

    ocsf_type: str
    sqlalchemy_type: str
    sqlalchemy_import: str
    postgres_type: str
    category: OcsfTypeCategory
    is_nullable_default: bool = True
    max_length: int | None = None

    def get_column_definition(self, nullable: bool | None = None) -> str:
        """Generate SQLAlchemy column type string."""
        if self.max_length:
            return f"{self.sqlalchemy_type}({self.max_length})"
        return self.sqlalchemy_type


class TypeMapper:
    """Maps OCSF schema types to SQLAlchemy and PostgreSQL types.

    This class handles the translation of OCSF's type system to appropriate
    SQLAlchemy column types for PostgreSQL, including:
    - Primitive types (string, integer, boolean, etc.)
    - Network types (IP addresses, MAC addresses, subnets)
    - Temporal types (timestamps, datetimes)
    - Special types (JSON, UUID)
    """

    # Type mapping table: OCSF type -> TypeMapping
    TYPE_MAPPINGS: dict[str, TypeMapping] = {
        # Primitive types
        "string_t": TypeMapping(
            ocsf_type="string_t",
            sqlalchemy_type="Text",
            sqlalchemy_import="from sqlalchemy import Text",
            postgres_type="TEXT",
            category=OcsfTypeCategory.PRIMITIVE,
        ),
        "integer_t": TypeMapping(
            ocsf_type="integer_t",
            sqlalchemy_type="Integer",
            sqlalchemy_import="from sqlalchemy import Integer",
            postgres_type="INTEGER",
            category=OcsfTypeCategory.PRIMITIVE,
        ),
        "long_t": TypeMapping(
            ocsf_type="long_t",
            sqlalchemy_type="BigInteger",
            sqlalchemy_import="from sqlalchemy import BigInteger",
            postgres_type="BIGINT",
            category=OcsfTypeCategory.PRIMITIVE,
        ),
        "float_t": TypeMapping(
            ocsf_type="float_t",
            sqlalchemy_type="Float",
            sqlalchemy_import="from sqlalchemy import Float",
            postgres_type="REAL",
            category=OcsfTypeCategory.PRIMITIVE,
        ),
        "boolean_t": TypeMapping(
            ocsf_type="boolean_t",
            sqlalchemy_type="Boolean",
            sqlalchemy_import="from sqlalchemy import Boolean",
            postgres_type="BOOLEAN",
            category=OcsfTypeCategory.PRIMITIVE,
        ),

        # Temporal types
        "timestamp_t": TypeMapping(
            ocsf_type="timestamp_t",
            sqlalchemy_type="BigInteger",
            sqlalchemy_import="from sqlalchemy import BigInteger",
            postgres_type="BIGINT",  # Milliseconds since epoch
            category=OcsfTypeCategory.TEMPORAL,
        ),
        "datetime_t": TypeMapping(
            ocsf_type="datetime_t",
            sqlalchemy_type="DateTime",
            sqlalchemy_import="from sqlalchemy import DateTime",
            postgres_type="TIMESTAMP WITH TIME ZONE",
            category=OcsfTypeCategory.TEMPORAL,
        ),

        # Network types - PostgreSQL native types
        "ip_t": TypeMapping(
            ocsf_type="ip_t",
            sqlalchemy_type="INET",
            sqlalchemy_import="from sqlalchemy.dialects.postgresql import INET",
            postgres_type="INET",
            category=OcsfTypeCategory.NETWORK,
        ),
        "mac_t": TypeMapping(
            ocsf_type="mac_t",
            sqlalchemy_type="String",
            sqlalchemy_import="from sqlalchemy import String",
            postgres_type="VARCHAR(17)",
            category=OcsfTypeCategory.NETWORK,
            max_length=17,
        ),
        "subnet_t": TypeMapping(
            ocsf_type="subnet_t",
            sqlalchemy_type="CIDR",
            sqlalchemy_import="from sqlalchemy.dialects.postgresql import CIDR",
            postgres_type="CIDR",
            category=OcsfTypeCategory.NETWORK,
        ),
        "port_t": TypeMapping(
            ocsf_type="port_t",
            sqlalchemy_type="Integer",
            sqlalchemy_import="from sqlalchemy import Integer",
            postgres_type="INTEGER",
            category=OcsfTypeCategory.NETWORK,
        ),
        "hostname_t": TypeMapping(
            ocsf_type="hostname_t",
            sqlalchemy_type="String",
            sqlalchemy_import="from sqlalchemy import String",
            postgres_type="VARCHAR(253)",
            category=OcsfTypeCategory.NETWORK,
            max_length=253,  # RFC 1035 max hostname length
        ),
        "email_t": TypeMapping(
            ocsf_type="email_t",
            sqlalchemy_type="String",
            sqlalchemy_import="from sqlalchemy import String",
            postgres_type="VARCHAR(254)",
            category=OcsfTypeCategory.NETWORK,
            max_length=254,  # RFC 5321 max email length
        ),
        "url_t": TypeMapping(
            ocsf_type="url_t",
            sqlalchemy_type="Text",
            sqlalchemy_import="from sqlalchemy import Text",
            postgres_type="TEXT",
            category=OcsfTypeCategory.NETWORK,
        ),

        # Special types
        "json_t": TypeMapping(
            ocsf_type="json_t",
            sqlalchemy_type="Text",
            sqlalchemy_import="from sqlalchemy import Text",
            postgres_type="TEXT",  # JSON stored as text per plan (no JSONB)
            category=OcsfTypeCategory.SPECIAL,
        ),
        "uuid_t": TypeMapping(
            ocsf_type="uuid_t",
            sqlalchemy_type="Uuid",
            sqlalchemy_import="from sqlalchemy import Uuid",
            postgres_type="UUID",
            category=OcsfTypeCategory.SPECIAL,
        ),

        # Path and file types
        "path_t": TypeMapping(
            ocsf_type="path_t",
            sqlalchemy_type="Text",
            sqlalchemy_import="from sqlalchemy import Text",
            postgres_type="TEXT",
            category=OcsfTypeCategory.PRIMITIVE,
        ),
        "file_hash_t": TypeMapping(
            ocsf_type="file_hash_t",
            sqlalchemy_type="String",
            sqlalchemy_import="from sqlalchemy import String",
            postgres_type="VARCHAR(128)",  # SHA-512 hex = 128 chars
            category=OcsfTypeCategory.PRIMITIVE,
            max_length=128,
        ),

        # Byte/binary types
        "bytestring_t": TypeMapping(
            ocsf_type="bytestring_t",
            sqlalchemy_type="LargeBinary",
            sqlalchemy_import="from sqlalchemy import LargeBinary",
            postgres_type="BYTEA",
            category=OcsfTypeCategory.PRIMITIVE,
        ),
    }

    # Default type for unknown OCSF types
    DEFAULT_MAPPING = TypeMapping(
        ocsf_type="unknown",
        sqlalchemy_type="Text",
        sqlalchemy_import="from sqlalchemy import Text",
        postgres_type="TEXT",
        category=OcsfTypeCategory.PRIMITIVE,
    )

    def __init__(self) -> None:
        """Initialize the type mapper."""
        self._custom_mappings: dict[str, TypeMapping] = {}

    def get_mapping(self, ocsf_type: str) -> TypeMapping:
        """Get the SQLAlchemy type mapping for an OCSF type.

        Args:
            ocsf_type: The OCSF type name (e.g., 'string_t', 'ip_t')

        Returns:
            TypeMapping with SQLAlchemy type information
        """
        # Check custom mappings first
        if ocsf_type in self._custom_mappings:
            return self._custom_mappings[ocsf_type]

        # Check built-in mappings
        if ocsf_type in self.TYPE_MAPPINGS:
            return self.TYPE_MAPPINGS[ocsf_type]

        # Return default for unknown types
        return self.DEFAULT_MAPPING

    def register_custom_mapping(self, mapping: TypeMapping) -> None:
        """Register a custom type mapping.

        Args:
            mapping: The TypeMapping to register
        """
        self._custom_mappings[mapping.ocsf_type] = mapping

    def get_sqlalchemy_type(self, ocsf_type: str) -> str:
        """Get the SQLAlchemy type string for an OCSF type.

        Args:
            ocsf_type: The OCSF type name

        Returns:
            SQLAlchemy type string (e.g., 'Integer', 'String(17)')
        """
        mapping = self.get_mapping(ocsf_type)
        return mapping.get_column_definition()

    def get_postgres_type(self, ocsf_type: str) -> str:
        """Get the PostgreSQL type for an OCSF type.

        Args:
            ocsf_type: The OCSF type name

        Returns:
            PostgreSQL type string (e.g., 'INTEGER', 'INET')
        """
        return self.get_mapping(ocsf_type).postgres_type

    def get_required_imports(self, ocsf_types: list[str]) -> set[str]:
        """Get all required SQLAlchemy imports for a list of OCSF types.

        Args:
            ocsf_types: List of OCSF type names

        Returns:
            Set of import statements needed
        """
        imports = set()
        for ocsf_type in ocsf_types:
            mapping = self.get_mapping(ocsf_type)
            imports.add(mapping.sqlalchemy_import)
        return imports

    def is_object_type(self, ocsf_type: str) -> bool:
        """Check if the OCSF type is an object reference (not a primitive).

        Object types require foreign key relationships rather than simple columns.

        Args:
            ocsf_type: The OCSF type name

        Returns:
            True if this is an object type requiring FK relationship
        """
        # Object types in OCSF don't end with _t and reference object schemas
        return not ocsf_type.endswith("_t") and ocsf_type not in self.TYPE_MAPPINGS

    def is_array_type(self, ocsf_type: str, is_array: bool) -> bool:
        """Check if the attribute represents an array.

        Arrays require separate association tables per the normalization strategy.

        Args:
            ocsf_type: The OCSF type name
            is_array: Whether the attribute is marked as an array in the schema

        Returns:
            True if this requires an association table
        """
        return is_array

    @classmethod
    def get_all_primitive_types(cls) -> list[str]:
        """Get list of all known primitive OCSF types."""
        return list(cls.TYPE_MAPPINGS.keys())

    @classmethod
    def get_types_by_category(cls, category: OcsfTypeCategory) -> list[str]:
        """Get list of OCSF types in a specific category.

        Args:
            category: The category to filter by

        Returns:
            List of OCSF type names in that category
        """
        return [
            type_name
            for type_name, mapping in cls.TYPE_MAPPINGS.items()
            if mapping.category == category
        ]
