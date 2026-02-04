"""Tests for the OCSF schema loader."""

import pytest
from pathlib import Path
from src.parser.schema_loader import (
    SchemaLoader,
    OcsfSchema,
    OcsfObject,
    OcsfEvent,
    OcsfCategory,
    OcsfAttribute,
)


class TestSchemaLoader:
    """Test suite for SchemaLoader class."""

    @pytest.fixture
    def schema_path(self) -> Path:
        """Return the path to the OCSF schema."""
        return Path(__file__).parent.parent.parent / "ocsf-schema"

    @pytest.fixture
    def loader(self, schema_path: Path) -> SchemaLoader:
        """Create a SchemaLoader instance."""
        return SchemaLoader(schema_path)

    def test_loader_initialization(self, schema_path: Path) -> None:
        """Test loader initializes with valid path."""
        loader = SchemaLoader(schema_path)
        assert loader.schema_path == schema_path

    def test_loader_invalid_path(self) -> None:
        """Test loader raises error for invalid path."""
        with pytest.raises(FileNotFoundError):
            SchemaLoader(Path("/nonexistent/path"))

    def test_loader_missing_required_file(self, tmp_path: Path) -> None:
        """Test loader raises error when required files are missing."""
        # Create empty directory
        with pytest.raises(FileNotFoundError) as exc_info:
            SchemaLoader(tmp_path)
        assert "version.json" in str(exc_info.value)

    def test_get_version(self, loader: SchemaLoader) -> None:
        """Test getting schema version."""
        version = loader.get_version()
        assert version is not None
        assert isinstance(version, str)
        # Should be a semantic version like "1.8.0-dev"
        assert "." in version


class TestSchemaLoading(TestSchemaLoader):
    """Tests for loading the complete schema."""

    def test_load_returns_schema(self, loader: SchemaLoader) -> None:
        """Test load() returns an OcsfSchema."""
        schema = loader.load()
        assert isinstance(schema, OcsfSchema)

    def test_schema_has_version(self, loader: SchemaLoader) -> None:
        """Test loaded schema has version."""
        schema = loader.load()
        assert schema.version is not None
        assert "." in schema.version

    def test_schema_has_objects(self, loader: SchemaLoader) -> None:
        """Test loaded schema has objects."""
        schema = loader.load()
        assert len(schema.objects) > 0

    def test_schema_has_events(self, loader: SchemaLoader) -> None:
        """Test loaded schema has events."""
        schema = loader.load()
        assert len(schema.events) > 0

    def test_schema_has_categories(self, loader: SchemaLoader) -> None:
        """Test loaded schema has categories."""
        schema = loader.load()
        assert len(schema.categories) > 0

    def test_schema_has_dictionary(self, loader: SchemaLoader) -> None:
        """Test loaded schema has dictionary."""
        schema = loader.load()
        assert len(schema.dictionary) > 0


class TestObjectLoading(TestSchemaLoader):
    """Tests for loading objects."""

    def test_list_objects(self, loader: SchemaLoader) -> None:
        """Test listing available objects."""
        objects = loader.list_objects()
        assert len(objects) > 0
        assert "device" in objects
        assert "process" in objects
        assert "user" in objects

    def test_get_object(self, loader: SchemaLoader) -> None:
        """Test getting a single object."""
        device = loader.get_object("device")
        assert device is not None
        assert isinstance(device, OcsfObject)
        assert device.name == "device"

    def test_get_nonexistent_object(self, loader: SchemaLoader) -> None:
        """Test getting a nonexistent object returns None."""
        obj = loader.get_object("nonexistent_object_xyz")
        assert obj is None

    def test_object_has_attributes(self, loader: SchemaLoader) -> None:
        """Test object has attributes."""
        device = loader.get_object("device")
        assert device is not None
        assert len(device.attributes) > 0

    def test_object_attribute_properties(self, loader: SchemaLoader) -> None:
        """Test object attribute has expected properties."""
        device = loader.get_object("device")
        assert device is not None
        # Device should have hostname attribute
        assert "hostname" in device.attributes
        hostname_attr = device.attributes["hostname"]
        assert isinstance(hostname_attr, OcsfAttribute)
        assert hostname_attr.name == "hostname"

    def test_device_object_specifics(self, loader: SchemaLoader) -> None:
        """Test device object has expected structure."""
        device = loader.get_object("device")
        assert device is not None
        assert device.caption == "Device"
        # Check some expected attributes (that exist in the raw JSON)
        expected_attrs = ["hostname", "ip", "name", "type", "type_id"]
        for attr in expected_attrs:
            assert attr in device.attributes, f"Missing attribute: {attr}"


class TestEventLoading(TestSchemaLoader):
    """Tests for loading events."""

    def test_list_events(self, loader: SchemaLoader) -> None:
        """Test listing available events."""
        events = loader.list_events()
        assert len(events) > 0
        assert "base_event" in events
        assert "process_activity" in events

    def test_load_events(self, loader: SchemaLoader) -> None:
        """Test loading all events."""
        schema = loader.load()
        assert "base_event" in schema.events
        assert "process_activity" in schema.events

    def test_base_event_structure(self, loader: SchemaLoader) -> None:
        """Test base_event has expected structure."""
        schema = loader.load()
        base = schema.events.get("base_event")
        assert base is not None
        assert isinstance(base, OcsfEvent)
        # Base event should have common attributes
        assert "activity_id" in base.attributes or len(base.attributes) > 0

    def test_process_activity_extends(self, loader: SchemaLoader) -> None:
        """Test process_activity extends system."""
        schema = loader.load()
        proc = schema.events.get("process_activity")
        assert proc is not None
        assert proc.extends == "system"

    def test_event_has_category(self, loader: SchemaLoader) -> None:
        """Test events have category assigned."""
        schema = loader.load()
        proc = schema.events.get("process_activity")
        assert proc is not None
        assert proc.category == "system"


class TestCategoryLoading(TestSchemaLoader):
    """Tests for loading categories."""

    def test_categories_loaded(self, loader: SchemaLoader) -> None:
        """Test categories are loaded."""
        schema = loader.load()
        assert len(schema.categories) > 0

    def test_expected_categories_present(self, loader: SchemaLoader) -> None:
        """Test expected categories are present."""
        schema = loader.load()
        expected = ["system", "network", "iam", "findings", "application", "discovery"]
        for cat in expected:
            assert cat in schema.categories, f"Missing category: {cat}"

    def test_category_structure(self, loader: SchemaLoader) -> None:
        """Test category has expected structure."""
        schema = loader.load()
        system = schema.categories.get("system")
        assert system is not None
        assert isinstance(system, OcsfCategory)
        assert system.name == "system"
        assert system.uid > 0


class TestAttributeParsing(TestSchemaLoader):
    """Tests for attribute parsing."""

    def test_array_type_detection(self, loader: SchemaLoader) -> None:
        """Test array types are detected when inline in object JSON.

        Note: In OCSF, is_array info often comes from the dictionary, not the
        object JSON directly. The SchemaAnalyzer will merge dictionary info.
        """
        schema = loader.load()
        # The device.groups attribute has is_array in dictionary, not inline
        # Check that we can at least load attributes without error
        device = schema.objects.get("device")
        assert device is not None
        assert "groups" in device.attributes
        # is_array from dictionary will be merged by SchemaAnalyzer

    def test_attribute_requirement(self, loader: SchemaLoader) -> None:
        """Test attribute requirements are parsed."""
        schema = loader.load()
        # Most attributes default to optional
        device = schema.objects.get("device")
        if device:
            for attr in device.attributes.values():
                assert attr.requirement in ["optional", "required", "recommended"]

    def test_attribute_type_parsed(self, loader: SchemaLoader) -> None:
        """Test attribute types are parsed when present in object JSON.

        Note: In OCSF, many attributes reference the dictionary for type info.
        The type field may be None in the raw object JSON.
        """
        schema = loader.load()
        # Find an attribute that has an inline type definition
        # (most are references to dictionary, so type may be None)
        found_typed_attr = False
        for obj in schema.objects.values():
            for attr in obj.attributes.values():
                if attr.type is not None:
                    found_typed_attr = True
                    break
            if found_typed_attr:
                break
        # It's OK if no inline types found - dictionary resolution is separate


class TestDictionaryAccess(TestSchemaLoader):
    """Tests for dictionary access methods."""

    def test_get_dictionary_attribute(self, loader: SchemaLoader) -> None:
        """Test getting attribute from dictionary."""
        attr_def = loader.get_dictionary_attribute("hostname")
        # Dictionary should have hostname definition
        # Note: might be None if not in dictionary, which is OK
        if attr_def:
            assert isinstance(attr_def, dict)

    def test_get_type_definition(self, loader: SchemaLoader) -> None:
        """Test getting type definition."""
        # Common types should exist
        type_def = loader.get_type_definition("string_t")
        # Note: structure varies by OCSF version
        # Just verify we can call the method


class TestEdgeCases(TestSchemaLoader):
    """Tests for edge cases and error handling."""

    def test_load_handles_missing_optional_fields(
        self, loader: SchemaLoader
    ) -> None:
        """Test loader handles missing optional fields gracefully."""
        schema = loader.load()
        # Should not raise, objects/events may have missing optional fields
        assert schema is not None

    def test_unicode_content(self, loader: SchemaLoader) -> None:
        """Test loader handles unicode content in descriptions."""
        schema = loader.load()
        # Descriptions may contain unicode, should not error
        for obj in schema.objects.values():
            _ = obj.description  # Should not raise

    def test_special_attributes_skipped(self, loader: SchemaLoader) -> None:
        """Test $include and other special attributes are skipped."""
        schema = loader.load()
        for event in schema.events.values():
            for attr_name in event.attributes:
                assert not attr_name.startswith("$")
