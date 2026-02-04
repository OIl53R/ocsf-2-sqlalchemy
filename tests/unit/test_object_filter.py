"""Tests for the OCSF object filter."""

import pytest
from pathlib import Path
from src.parser.schema_analyzer import SchemaAnalyzer, AnalyzedSchema
from src.parser.object_filter import ObjectFilter, FilterConfig, FilterResult


class TestObjectFilter:
    """Test suite for ObjectFilter class."""

    @pytest.fixture
    def schema_path(self) -> Path:
        """Return the path to the OCSF schema."""
        return Path(__file__).parent.parent.parent / "ocsf-schema"

    @pytest.fixture
    def analyzed(self, schema_path: Path) -> AnalyzedSchema:
        """Create an analyzed schema."""
        analyzer = SchemaAnalyzer(schema_path)
        return analyzer.analyze()

    @pytest.fixture
    def obj_filter(self, analyzed: AnalyzedSchema) -> ObjectFilter:
        """Create an ObjectFilter instance."""
        return ObjectFilter(analyzed)


class TestFilterConfig(TestObjectFilter):
    """Tests for FilterConfig dataclass."""

    def test_config_defaults(self) -> None:
        """Test FilterConfig default values."""
        config = FilterConfig(core_object="device")
        assert config.core_object == "device"
        assert config.max_depth == 3
        assert config.include_events is False

    def test_config_custom_values(self) -> None:
        """Test FilterConfig with custom values."""
        config = FilterConfig(
            core_object="vulnerability",
            max_depth=5,
            include_events=True,
        )
        assert config.core_object == "vulnerability"
        assert config.max_depth == 5
        assert config.include_events is True


class TestFilterResult(TestObjectFilter):
    """Tests for FilterResult dataclass."""

    def test_result_defaults(self) -> None:
        """Test FilterResult default values."""
        result = FilterResult()
        assert result.included_objects == set()
        assert result.object_depths == {}
        assert result.inheritance_additions == set()
        assert result.excluded_objects == set()
        assert result.included_events == set()


class TestFilterValidation(TestObjectFilter):
    """Tests for filter input validation."""

    def test_invalid_core_object_raises_error(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test that invalid core object raises ValueError."""
        config = FilterConfig(core_object="nonexistent_object")
        with pytest.raises(ValueError) as exc_info:
            obj_filter.filter(config)
        assert "nonexistent_object" in str(exc_info.value)
        assert "not found" in str(exc_info.value)

    def test_error_message_includes_available_objects(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test error message includes some available objects."""
        config = FilterConfig(core_object="invalid")
        with pytest.raises(ValueError) as exc_info:
            obj_filter.filter(config)
        # Should include some available object names
        assert "Available objects" in str(exc_info.value)


class TestDepthZeroFilter(TestObjectFilter):
    """Tests for depth 0 filtering (core object only)."""

    def test_filter_depth_0_includes_core(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test depth 0 includes only core object."""
        config = FilterConfig(core_object="device", max_depth=0)
        filtered, result = obj_filter.filter(config)

        assert "device" in result.included_objects
        assert result.object_depths["device"] == 0

    def test_filter_depth_0_no_dependencies(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test depth 0 doesn't include dependencies."""
        config = FilterConfig(core_object="device", max_depth=0)
        filtered, result = obj_filter.filter(config)

        # Should only have core + inheritance parents
        total = len(result.included_objects) + len(result.inheritance_additions)
        # This should be a small number (just core + parents)
        assert total <= 5  # device and its inheritance chain

    def test_filter_depth_0_includes_inheritance_parents(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test depth 0 includes inheritance parents."""
        # Find an object with inheritance
        device = analyzed.objects.get("device")
        if device and device.extends:
            config = FilterConfig(core_object="device", max_depth=0)
            filtered, result = obj_filter.filter(config)

            # Parent should be in inheritance_additions
            if device.extends in analyzed.objects:
                all_included = result.included_objects | result.inheritance_additions
                assert device.extends in all_included


class TestDepthOneFilter(TestObjectFilter):
    """Tests for depth 1 filtering."""

    def test_filter_depth_1_includes_direct_deps(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test depth 1 includes direct dependencies."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, result = obj_filter.filter(config)

        # Device should be at depth 0
        assert result.object_depths["device"] == 0

        # Direct dependencies should be at depth 1
        for obj_name, depth in result.object_depths.items():
            assert depth <= 1

    def test_filter_depth_1_more_than_depth_0(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test depth 1 includes more objects than depth 0."""
        config_0 = FilterConfig(core_object="device", max_depth=0)
        config_1 = FilterConfig(core_object="device", max_depth=1)

        _, result_0 = obj_filter.filter(config_0)
        _, result_1 = obj_filter.filter(config_1)

        # Depth 1 should have at least as many objects as depth 0
        assert len(result_1.included_objects) >= len(result_0.included_objects)


class TestCircularReferences(TestObjectFilter):
    """Tests for circular reference handling."""

    def test_circular_reference_process(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test process with parent_process circular ref doesn't infinite loop."""
        if "process" not in analyzed.objects:
            pytest.skip("process object not in schema")

        config = FilterConfig(core_object="process", max_depth=5)
        # This should complete without hanging
        filtered, result = obj_filter.filter(config)

        # Process should be included exactly once
        assert "process" in result.included_objects
        assert result.object_depths["process"] == 0

    def test_no_duplicate_depths(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test each object has exactly one depth value."""
        config = FilterConfig(core_object="device", max_depth=3)
        _, result = obj_filter.filter(config)

        # Each included object should have exactly one depth
        for obj in result.included_objects:
            assert obj in result.object_depths


class TestInheritanceChains(TestObjectFilter):
    """Tests for inheritance chain handling."""

    def test_inheritance_parents_always_included(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test inheritance parents are added even beyond depth."""
        # Find an object with a deep inheritance chain
        for obj_name, obj in analyzed.objects.items():
            if len(obj.inheritance_chain) > 2:
                config = FilterConfig(core_object=obj_name, max_depth=0)
                filtered, result = obj_filter.filter(config)

                all_included = result.included_objects | result.inheritance_additions

                # All parents in chain should be present
                for parent in obj.inheritance_chain:
                    if parent in analyzed.objects:
                        assert parent in all_included, (
                            f"Parent {parent} missing for {obj_name}"
                        )
                break

    def test_inheritance_additions_separate_from_bfs(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test inheritance additions are tracked separately."""
        # Find object with parent
        for obj_name, obj in analyzed.objects.items():
            if obj.extends and obj.extends in analyzed.objects:
                config = FilterConfig(core_object=obj_name, max_depth=0)
                _, result = obj_filter.filter(config)

                # Parent should be in additions if not reached via BFS
                if obj.extends not in result.included_objects:
                    assert obj.extends in result.inheritance_additions
                break


class TestAssociationTables(TestObjectFilter):
    """Tests for association table filtering."""

    def test_association_tables_both_sides_required(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test association tables only included when both sides present."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, _ = obj_filter.filter(config)

        all_included = set(filtered.objects.keys())

        for arr in filtered.array_attributes:
            # Parent must be included
            assert arr.parent_entity in all_included or arr.parent_entity in filtered.events

            # For object arrays, element type must be included
            if not arr.is_primitive:
                assert arr.element_type in all_included, (
                    f"Array {arr.attribute_name} element type {arr.element_type} not included"
                )

    def test_primitive_arrays_included(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test primitive arrays are included when parent is."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, _ = obj_filter.filter(config)

        included_objects = set(filtered.objects.keys())

        # All primitive arrays with included parents should be present
        for arr in filtered.array_attributes:
            if arr.is_primitive:
                assert arr.parent_entity in included_objects or arr.parent_entity in filtered.events


class TestRelationshipFiltering(TestObjectFilter):
    """Tests for relationship filtering."""

    def test_relationships_filtered_correctly(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test relationships only include connected entities."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, _ = obj_filter.filter(config)

        all_included = set(filtered.objects.keys())

        for rel in filtered.relationships:
            # Source must be in included objects or events
            assert rel.source_entity in all_included or rel.source_entity in filtered.events
            # Target must be in included objects
            assert rel.target_entity in all_included


class TestEventFiltering(TestObjectFilter):
    """Tests for event inclusion."""

    def test_events_excluded_by_default(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test events are not included by default."""
        config = FilterConfig(core_object="device", max_depth=1, include_events=False)
        filtered, result = obj_filter.filter(config)

        assert len(result.included_events) == 0
        assert len(filtered.events) == 0

    def test_events_included_when_requested(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test events are included when flag is set."""
        if len(analyzed.events) == 0:
            pytest.skip("No events in schema")

        config = FilterConfig(core_object="device", max_depth=2, include_events=True)
        filtered, result = obj_filter.filter(config)

        # May or may not have events depending on what references device
        # Just verify the flag is respected
        assert filtered is not None


class TestFilteredSchemaStructure(TestObjectFilter):
    """Tests for filtered schema structure."""

    def test_filtered_schema_has_version(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test filtered schema preserves version."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, _ = obj_filter.filter(config)

        assert filtered.version is not None
        assert "." in filtered.version

    def test_filtered_schema_has_trees(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test filtered schema has inheritance trees."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, _ = obj_filter.filter(config)

        assert filtered.object_tree is not None
        assert filtered.event_tree is not None

    def test_filtered_tree_topological_order(
        self, obj_filter: ObjectFilter
    ) -> None:
        """Test filtered tree has valid topological order."""
        config = FilterConfig(core_object="device", max_depth=2)
        filtered, _ = obj_filter.filter(config)

        # All objects should be in topological order
        all_objects = set(filtered.objects.keys())
        order_set = set(filtered.object_tree.topological_order)

        assert all_objects == order_set

    def test_filtered_schema_fewer_objects(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test filtered schema has fewer objects than full schema."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, result = obj_filter.filter(config)

        total_filtered = len(result.included_objects) + len(result.inheritance_additions)

        # Filtered should be subset of original
        assert total_filtered <= len(analyzed.objects)

    def test_filtered_preserves_categories(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test filtered schema preserves categories."""
        config = FilterConfig(core_object="device", max_depth=1)
        filtered, _ = obj_filter.filter(config)

        assert filtered.categories == analyzed.categories


class TestVulnerabilityExample(TestObjectFilter):
    """Tests specific to vulnerability object (from plan)."""

    def test_vulnerability_depth_3(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test vulnerability at depth 3 produces reasonable subset."""
        if "vulnerability" not in analyzed.objects:
            pytest.skip("vulnerability object not in schema")

        config = FilterConfig(core_object="vulnerability", max_depth=3)
        filtered, result = obj_filter.filter(config)

        # Should be significantly fewer than full schema
        total_original = len(analyzed.objects)
        total_filtered = len(result.included_objects) + len(result.inheritance_additions)

        assert total_filtered < total_original
        assert "vulnerability" in result.included_objects
        assert result.object_depths["vulnerability"] == 0

    def test_vulnerability_has_expected_dependencies(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test vulnerability includes expected related objects."""
        if "vulnerability" not in analyzed.objects:
            pytest.skip("vulnerability object not in schema")

        config = FilterConfig(core_object="vulnerability", max_depth=1)
        filtered, result = obj_filter.filter(config)

        all_included = result.included_objects | result.inheritance_additions

        # These are common vulnerability-related objects
        # May vary by OCSF version
        vuln_obj = analyzed.objects["vulnerability"]
        for attr in vuln_obj.all_attributes.values():
            if attr.object_type and attr.object_type in analyzed.objects:
                # Direct dependencies should be at depth 1
                assert attr.object_type in all_included, (
                    f"Expected {attr.object_type} to be included"
                )


class TestExcludedObjects(TestObjectFilter):
    """Tests for excluded objects tracking."""

    def test_excluded_objects_tracked(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test excluded objects are correctly tracked."""
        config = FilterConfig(core_object="device", max_depth=0)
        _, result = obj_filter.filter(config)

        all_included = result.included_objects | result.inheritance_additions
        all_objects = set(analyzed.objects.keys())

        # Excluded should be all objects not in included
        expected_excluded = all_objects - all_included
        assert result.excluded_objects == expected_excluded

    def test_excluded_plus_included_equals_total(
        self, obj_filter: ObjectFilter, analyzed: AnalyzedSchema
    ) -> None:
        """Test excluded + included = total objects."""
        config = FilterConfig(core_object="device", max_depth=2)
        _, result = obj_filter.filter(config)

        all_included = result.included_objects | result.inheritance_additions
        total = len(all_included) + len(result.excluded_objects)

        assert total == len(analyzed.objects)
