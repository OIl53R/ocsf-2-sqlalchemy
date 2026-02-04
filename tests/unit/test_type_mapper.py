"""Tests for the OCSF to SQLAlchemy type mapper."""

import pytest
from src.parser.type_mapper import TypeMapper, TypeMapping, OcsfTypeCategory


class TestTypeMapper:
    """Test suite for TypeMapper class."""

    @pytest.fixture
    def mapper(self) -> TypeMapper:
        """Create a fresh TypeMapper instance."""
        return TypeMapper()

    # Primitive type tests
    def test_string_type_mapping(self, mapper: TypeMapper) -> None:
        """Test string_t maps to Text."""
        mapping = mapper.get_mapping("string_t")
        assert mapping.sqlalchemy_type == "Text"
        assert mapping.postgres_type == "TEXT"
        assert mapping.category == OcsfTypeCategory.PRIMITIVE

    def test_integer_type_mapping(self, mapper: TypeMapper) -> None:
        """Test integer_t maps to Integer."""
        mapping = mapper.get_mapping("integer_t")
        assert mapping.sqlalchemy_type == "Integer"
        assert mapping.postgres_type == "INTEGER"

    def test_long_type_mapping(self, mapper: TypeMapper) -> None:
        """Test long_t maps to BigInteger."""
        mapping = mapper.get_mapping("long_t")
        assert mapping.sqlalchemy_type == "BigInteger"
        assert mapping.postgres_type == "BIGINT"

    def test_float_type_mapping(self, mapper: TypeMapper) -> None:
        """Test float_t maps to Float."""
        mapping = mapper.get_mapping("float_t")
        assert mapping.sqlalchemy_type == "Float"
        assert mapping.postgres_type == "REAL"

    def test_boolean_type_mapping(self, mapper: TypeMapper) -> None:
        """Test boolean_t maps to Boolean."""
        mapping = mapper.get_mapping("boolean_t")
        assert mapping.sqlalchemy_type == "Boolean"
        assert mapping.postgres_type == "BOOLEAN"

    # Temporal type tests
    def test_timestamp_type_mapping(self, mapper: TypeMapper) -> None:
        """Test timestamp_t maps to BigInteger (ms since epoch)."""
        mapping = mapper.get_mapping("timestamp_t")
        assert mapping.sqlalchemy_type == "BigInteger"
        assert mapping.postgres_type == "BIGINT"
        assert mapping.category == OcsfTypeCategory.TEMPORAL

    def test_datetime_type_mapping(self, mapper: TypeMapper) -> None:
        """Test datetime_t maps to DateTime."""
        mapping = mapper.get_mapping("datetime_t")
        assert mapping.sqlalchemy_type == "DateTime"
        assert "TIMESTAMP" in mapping.postgres_type

    # Network type tests
    def test_ip_type_mapping(self, mapper: TypeMapper) -> None:
        """Test ip_t maps to INET (PostgreSQL native)."""
        mapping = mapper.get_mapping("ip_t")
        assert mapping.sqlalchemy_type == "INET"
        assert mapping.postgres_type == "INET"
        assert mapping.category == OcsfTypeCategory.NETWORK

    def test_mac_type_mapping(self, mapper: TypeMapper) -> None:
        """Test mac_t maps to String(17)."""
        mapping = mapper.get_mapping("mac_t")
        assert mapping.sqlalchemy_type == "String"
        assert mapping.max_length == 17
        assert mapping.get_column_definition() == "String(17)"

    def test_subnet_type_mapping(self, mapper: TypeMapper) -> None:
        """Test subnet_t maps to CIDR."""
        mapping = mapper.get_mapping("subnet_t")
        assert mapping.sqlalchemy_type == "CIDR"
        assert mapping.postgres_type == "CIDR"

    def test_port_type_mapping(self, mapper: TypeMapper) -> None:
        """Test port_t maps to Integer."""
        mapping = mapper.get_mapping("port_t")
        assert mapping.sqlalchemy_type == "Integer"

    # Special type tests
    def test_json_type_mapping(self, mapper: TypeMapper) -> None:
        """Test json_t maps to Text (not JSONB per plan)."""
        mapping = mapper.get_mapping("json_t")
        assert mapping.sqlalchemy_type == "Text"
        assert mapping.postgres_type == "TEXT"
        assert mapping.category == OcsfTypeCategory.SPECIAL

    def test_uuid_type_mapping(self, mapper: TypeMapper) -> None:
        """Test uuid_t maps to Uuid."""
        mapping = mapper.get_mapping("uuid_t")
        assert mapping.sqlalchemy_type == "Uuid"
        assert mapping.postgres_type == "UUID"

    # Unknown type handling
    def test_unknown_type_returns_default(self, mapper: TypeMapper) -> None:
        """Test unknown types return default Text mapping."""
        mapping = mapper.get_mapping("unknown_custom_type")
        assert mapping.sqlalchemy_type == "Text"
        assert mapping.postgres_type == "TEXT"

    # Column definition tests
    def test_column_definition_without_length(self, mapper: TypeMapper) -> None:
        """Test column definition for types without length."""
        mapping = mapper.get_mapping("integer_t")
        assert mapping.get_column_definition() == "Integer"

    def test_column_definition_with_length(self, mapper: TypeMapper) -> None:
        """Test column definition for types with length."""
        mapping = mapper.get_mapping("mac_t")
        assert mapping.get_column_definition() == "String(17)"

    # Import generation tests
    def test_get_required_imports(self, mapper: TypeMapper) -> None:
        """Test collecting required imports for multiple types."""
        types = ["string_t", "integer_t", "ip_t"]
        imports = mapper.get_required_imports(types)

        assert "from sqlalchemy import Text" in imports
        assert "from sqlalchemy import Integer" in imports
        assert "from sqlalchemy.dialects.postgresql import INET" in imports

    def test_get_required_imports_deduplication(self, mapper: TypeMapper) -> None:
        """Test that duplicate imports are removed."""
        types = ["string_t", "string_t", "json_t"]  # Both map to Text
        imports = mapper.get_required_imports(types)

        text_imports = [i for i in imports if "Text" in i]
        assert len(text_imports) == 1

    # Object type detection tests
    def test_is_object_type_for_primitive(self, mapper: TypeMapper) -> None:
        """Test primitive types are not object types."""
        assert mapper.is_object_type("string_t") is False
        assert mapper.is_object_type("integer_t") is False

    def test_is_object_type_for_object(self, mapper: TypeMapper) -> None:
        """Test object references are detected."""
        assert mapper.is_object_type("device") is True
        assert mapper.is_object_type("process") is True
        assert mapper.is_object_type("user") is True

    # Array type detection tests
    def test_is_array_type(self, mapper: TypeMapper) -> None:
        """Test array detection."""
        assert mapper.is_array_type("string_t", is_array=True) is True
        assert mapper.is_array_type("string_t", is_array=False) is False

    # Custom mapping tests
    def test_register_custom_mapping(self, mapper: TypeMapper) -> None:
        """Test registering custom type mappings."""
        custom = TypeMapping(
            ocsf_type="custom_t",
            sqlalchemy_type="CustomType",
            sqlalchemy_import="from custom import CustomType",
            postgres_type="CUSTOM",
            category=OcsfTypeCategory.SPECIAL,
        )
        mapper.register_custom_mapping(custom)

        mapping = mapper.get_mapping("custom_t")
        assert mapping.sqlalchemy_type == "CustomType"

    def test_custom_mapping_overrides_default(self, mapper: TypeMapper) -> None:
        """Test custom mappings override built-in ones."""
        custom = TypeMapping(
            ocsf_type="string_t",
            sqlalchemy_type="VARCHAR",
            sqlalchemy_import="from sqlalchemy import VARCHAR",
            postgres_type="VARCHAR(1000)",
            category=OcsfTypeCategory.PRIMITIVE,
            max_length=1000,
        )
        mapper.register_custom_mapping(custom)

        mapping = mapper.get_mapping("string_t")
        assert mapping.sqlalchemy_type == "VARCHAR"

    # Category listing tests
    def test_get_all_primitive_types(self) -> None:
        """Test getting all known primitive types."""
        primitives = TypeMapper.get_all_primitive_types()
        assert "string_t" in primitives
        assert "integer_t" in primitives
        assert len(primitives) > 10

    def test_get_types_by_category(self) -> None:
        """Test filtering types by category."""
        network_types = TypeMapper.get_types_by_category(OcsfTypeCategory.NETWORK)
        assert "ip_t" in network_types
        assert "mac_t" in network_types
        assert "subnet_t" in network_types
        assert "string_t" not in network_types

    def test_get_temporal_types(self) -> None:
        """Test filtering temporal types."""
        temporal_types = TypeMapper.get_types_by_category(OcsfTypeCategory.TEMPORAL)
        assert "timestamp_t" in temporal_types
        assert "datetime_t" in temporal_types


class TestTypeMapping:
    """Test suite for TypeMapping dataclass."""

    def test_type_mapping_creation(self) -> None:
        """Test creating a TypeMapping."""
        mapping = TypeMapping(
            ocsf_type="test_t",
            sqlalchemy_type="Test",
            sqlalchemy_import="from test import Test",
            postgres_type="TEST",
            category=OcsfTypeCategory.PRIMITIVE,
        )
        assert mapping.ocsf_type == "test_t"
        assert mapping.is_nullable_default is True

    def test_type_mapping_with_length(self) -> None:
        """Test TypeMapping with max_length."""
        mapping = TypeMapping(
            ocsf_type="test_t",
            sqlalchemy_type="String",
            sqlalchemy_import="from sqlalchemy import String",
            postgres_type="VARCHAR(100)",
            category=OcsfTypeCategory.PRIMITIVE,
            max_length=100,
        )
        assert mapping.get_column_definition() == "String(100)"
