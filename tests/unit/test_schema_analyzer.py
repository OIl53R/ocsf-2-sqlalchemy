"""Tests for the OCSF schema analyzer."""

import pytest
from pathlib import Path
from src.parser.schema_analyzer import (
    SchemaAnalyzer,
    AnalyzedSchema,
    RelationshipInfo,
    ArrayAttributeInfo,
    EnumInfo,
)
from src.parser.type_mapper import TypeMapper


class TestSchemaAnalyzer:
    """Test suite for SchemaAnalyzer class."""

    @pytest.fixture
    def schema_path(self) -> Path:
        """Return the path to the OCSF schema."""
        return Path(__file__).parent.parent.parent / "ocsf-schema"

    @pytest.fixture
    def analyzer(self, schema_path: Path) -> SchemaAnalyzer:
        """Create a SchemaAnalyzer instance."""
        return SchemaAnalyzer(schema_path)


class TestAnalyzerInitialization(TestSchemaAnalyzer):
    """Tests for analyzer initialization."""

    def test_analyzer_creation(self, schema_path: Path) -> None:
        """Test analyzer can be created."""
        analyzer = SchemaAnalyzer(schema_path)
        assert analyzer is not None

    def test_analyzer_with_custom_type_mapper(self, schema_path: Path) -> None:
        """Test analyzer with custom type mapper."""
        mapper = TypeMapper()
        analyzer = SchemaAnalyzer(schema_path, type_mapper=mapper)
        assert analyzer.type_mapper is mapper

    def test_lazy_loading(self, analyzer: SchemaAnalyzer) -> None:
        """Test that schema is loaded lazily."""
        # Schema should not be loaded until accessed
        assert analyzer._schema is None
        # Access triggers load
        _ = analyzer.schema
        assert analyzer._schema is not None


class TestSchemaAnalysis(TestSchemaAnalyzer):
    """Tests for complete schema analysis."""

    def test_analyze_returns_analyzed_schema(self, analyzer: SchemaAnalyzer) -> None:
        """Test analyze() returns AnalyzedSchema."""
        result = analyzer.analyze()
        assert isinstance(result, AnalyzedSchema)

    def test_analyzed_schema_has_version(self, analyzer: SchemaAnalyzer) -> None:
        """Test analyzed schema has version."""
        result = analyzer.analyze()
        assert result.version is not None
        assert "." in result.version

    def test_analyzed_schema_has_objects(self, analyzer: SchemaAnalyzer) -> None:
        """Test analyzed schema has objects."""
        result = analyzer.analyze()
        assert len(result.objects) > 0
        assert "device" in result.objects

    def test_analyzed_schema_has_events(self, analyzer: SchemaAnalyzer) -> None:
        """Test analyzed schema has events."""
        result = analyzer.analyze()
        assert len(result.events) > 0
        assert "base_event" in result.events

    def test_analyzed_schema_has_trees(self, analyzer: SchemaAnalyzer) -> None:
        """Test analyzed schema has inheritance trees."""
        result = analyzer.analyze()
        assert result.object_tree is not None
        assert result.event_tree is not None

    def test_analyzed_schema_has_categories(self, analyzer: SchemaAnalyzer) -> None:
        """Test analyzed schema has categories."""
        result = analyzer.analyze()
        assert len(result.categories) > 0


class TestRelationshipAnalysis(TestSchemaAnalyzer):
    """Tests for relationship analysis."""

    def test_relationships_found(self, analyzer: SchemaAnalyzer) -> None:
        """Test that relationships are identified."""
        result = analyzer.analyze()
        assert isinstance(result.relationships, list)
        # Should find some relationships (objects referencing other objects)

    def test_relationship_info_structure(self, analyzer: SchemaAnalyzer) -> None:
        """Test RelationshipInfo has correct structure."""
        result = analyzer.analyze()
        if len(result.relationships) > 0:
            rel = result.relationships[0]
            assert isinstance(rel, RelationshipInfo)
            assert rel.source_entity is not None
            assert rel.attribute_name is not None
            assert rel.relationship_type in ["foreign_key", "association_table"]


class TestArrayAttributes(TestSchemaAnalyzer):
    """Tests for array attribute detection."""

    def test_array_attributes_found(self, analyzer: SchemaAnalyzer) -> None:
        """Test that array attributes are identified."""
        result = analyzer.analyze()
        assert isinstance(result.array_attributes, list)

    def test_array_info_structure(self, analyzer: SchemaAnalyzer) -> None:
        """Test ArrayAttributeInfo has correct structure."""
        result = analyzer.analyze()
        if len(result.array_attributes) > 0:
            arr = result.array_attributes[0]
            assert isinstance(arr, ArrayAttributeInfo)
            assert arr.parent_entity is not None
            assert arr.attribute_name is not None
            assert arr.association_table_name is not None
            assert arr.association_table_name.startswith("ocsf_")

    def test_groups_detected_as_array(self, analyzer: SchemaAnalyzer) -> None:
        """Test device.groups is detected as array."""
        result = analyzer.analyze()
        # Find groups array
        groups_arrays = [
            a for a in result.array_attributes
            if a.attribute_name == "groups" and a.parent_entity == "device"
        ]
        assert len(groups_arrays) > 0


class TestEnumExtraction(TestSchemaAnalyzer):
    """Tests for enum extraction."""

    def test_enums_extracted(self, analyzer: SchemaAnalyzer) -> None:
        """Test that enums are extracted."""
        result = analyzer.analyze()
        assert isinstance(result.enums, dict)

    def test_enum_structure(self, analyzer: SchemaAnalyzer) -> None:
        """Test EnumInfo has correct structure."""
        result = analyzer.analyze()
        if len(result.enums) > 0:
            enum_name, enum_info = next(iter(result.enums.items()))
            assert isinstance(enum_info, EnumInfo)
            assert enum_info.name is not None


class TestDependencyAnalysis(TestSchemaAnalyzer):
    """Tests for dependency analysis."""

    def test_get_object_dependencies(self, analyzer: SchemaAnalyzer) -> None:
        """Test getting object dependencies."""
        # Device likely references other objects (like user, location)
        deps = analyzer.get_object_dependencies("device")
        assert isinstance(deps, list)

    def test_generation_order(self, analyzer: SchemaAnalyzer) -> None:
        """Test getting generation order."""
        objects, events = analyzer.get_generation_order()
        assert isinstance(objects, list)
        assert isinstance(events, list)
        assert len(objects) > 0
        assert len(events) > 0


class TestColumnGeneration(TestSchemaAnalyzer):
    """Tests for column definition generation."""

    def test_get_entity_columns(self, analyzer: SchemaAnalyzer) -> None:
        """Test getting columns for an entity."""
        columns = analyzer.get_entity_columns("device", is_event=False)
        assert isinstance(columns, list)

    def test_column_structure(self, analyzer: SchemaAnalyzer) -> None:
        """Test column dict structure."""
        columns = analyzer.get_entity_columns("device", is_event=False)
        if len(columns) > 0:
            col = columns[0]
            assert "name" in col
            assert "type" in col
            assert "nullable" in col

    def test_event_columns(self, analyzer: SchemaAnalyzer) -> None:
        """Test getting columns for an event."""
        columns = analyzer.get_entity_columns("process_activity", is_event=True)
        assert isinstance(columns, list)

    def test_array_attributes_excluded_from_columns(
        self, analyzer: SchemaAnalyzer
    ) -> None:
        """Test array attributes are not included as columns."""
        columns = analyzer.get_entity_columns("device", is_event=False)
        column_names = [c["name"] for c in columns]
        # groups is an array, should not be a column
        assert "groups" not in column_names


class TestIntegration(TestSchemaAnalyzer):
    """Integration tests for schema analyzer."""

    def test_full_analysis_completes(self, analyzer: SchemaAnalyzer) -> None:
        """Test complete analysis without errors."""
        result = analyzer.analyze()
        assert result is not None

    def test_analysis_is_consistent(self, analyzer: SchemaAnalyzer) -> None:
        """Test multiple analysis calls return consistent results."""
        result1 = analyzer.analyze()
        result2 = analyzer.analyze()
        assert result1.version == result2.version
        assert len(result1.objects) == len(result2.objects)
        assert len(result1.events) == len(result2.events)

    def test_all_events_have_inheritance_chain(self, analyzer: SchemaAnalyzer) -> None:
        """Test all events have their inheritance chain resolved."""
        result = analyzer.analyze()
        for event_name, event in result.events.items():
            assert event.inheritance_chain is not None
            assert len(event.inheritance_chain) > 0
            assert event.inheritance_chain[0] == event_name
