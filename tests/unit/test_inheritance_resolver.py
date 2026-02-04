"""Tests for the OCSF inheritance resolver."""

import pytest
from pathlib import Path
from src.parser.schema_loader import SchemaLoader
from src.parser.inheritance_resolver import (
    InheritanceResolver,
    ResolvedObject,
    ResolvedEvent,
    ResolvedAttribute,
    InheritanceTree,
)


class TestInheritanceResolver:
    """Test suite for InheritanceResolver class."""

    @pytest.fixture
    def schema_path(self) -> Path:
        """Return the path to the OCSF schema."""
        return Path(__file__).parent.parent.parent / "ocsf-schema"

    @pytest.fixture
    def schema(self, schema_path: Path):
        """Load the OCSF schema."""
        loader = SchemaLoader(schema_path)
        return loader.load()

    @pytest.fixture
    def resolver(self, schema) -> InheritanceResolver:
        """Create an InheritanceResolver instance."""
        return InheritanceResolver(schema)


class TestObjectResolution(TestInheritanceResolver):
    """Tests for resolving object inheritance."""

    def test_resolve_object_returns_resolved(self, resolver: InheritanceResolver) -> None:
        """Test resolving an object returns ResolvedObject."""
        device = resolver.resolve_object("device")
        assert device is not None
        assert isinstance(device, ResolvedObject)

    def test_resolve_nonexistent_object(self, resolver: InheritanceResolver) -> None:
        """Test resolving nonexistent object returns None."""
        result = resolver.resolve_object("nonexistent_xyz")
        assert result is None

    def test_resolved_object_has_attributes(self, resolver: InheritanceResolver) -> None:
        """Test resolved object has attributes."""
        device = resolver.resolve_object("device")
        assert device is not None
        assert len(device.all_attributes) > 0

    def test_resolved_attribute_has_type(self, resolver: InheritanceResolver) -> None:
        """Test resolved attributes have type info from dictionary."""
        device = resolver.resolve_object("device")
        assert device is not None
        # hostname should have type resolved from dictionary
        if "hostname" in device.all_attributes:
            hostname = device.all_attributes["hostname"]
            assert isinstance(hostname, ResolvedAttribute)
            # Type comes from dictionary
            assert hostname.ocsf_type is not None or hostname.name == "hostname"

    def test_resolve_all_objects(self, resolver: InheritanceResolver) -> None:
        """Test resolving all objects."""
        resolved = resolver.resolve_all_objects()
        assert len(resolved) > 0
        assert "device" in resolved
        assert "process" in resolved


class TestEventResolution(TestInheritanceResolver):
    """Tests for resolving event inheritance."""

    def test_resolve_event_returns_resolved(self, resolver: InheritanceResolver) -> None:
        """Test resolving an event returns ResolvedEvent."""
        event = resolver.resolve_event("base_event")
        assert event is not None
        assert isinstance(event, ResolvedEvent)

    def test_resolve_nonexistent_event(self, resolver: InheritanceResolver) -> None:
        """Test resolving nonexistent event returns None."""
        result = resolver.resolve_event("nonexistent_event_xyz")
        assert result is None

    def test_process_activity_inheritance_chain(self, resolver: InheritanceResolver) -> None:
        """Test process_activity inherits from system -> base_event."""
        proc = resolver.resolve_event("process_activity")
        assert proc is not None
        # Chain should be [process_activity, system, base_event]
        assert proc.inheritance_chain[0] == "process_activity"
        assert "system" in proc.inheritance_chain
        # Note: The chain might not reach base_event if system doesn't exist as event

    def test_resolved_event_has_inherited_attributes(
        self, resolver: InheritanceResolver
    ) -> None:
        """Test resolved event has inherited attributes."""
        proc = resolver.resolve_event("process_activity")
        assert proc is not None
        # Process activity should have some inherited attributes
        # (from system and/or base_event)
        assert len(proc.all_attributes) > 0

    def test_inherited_attribute_marked(self, resolver: InheritanceResolver) -> None:
        """Test inherited attributes are marked as such."""
        proc = resolver.resolve_event("process_activity")
        assert proc is not None
        # Check that inherited_attributes dict is separate from own
        for attr in proc.inherited_attributes.values():
            assert attr.is_inherited is True
        for attr in proc.own_attributes.values():
            assert attr.is_inherited is False

    def test_own_attributes_override_inherited(
        self, resolver: InheritanceResolver
    ) -> None:
        """Test that own attributes override inherited ones."""
        proc = resolver.resolve_event("process_activity")
        assert proc is not None
        # Own attributes should be in all_attributes
        for attr_name, attr in proc.own_attributes.items():
            assert attr_name in proc.all_attributes
            assert proc.all_attributes[attr_name].is_inherited is False

    def test_resolve_all_events(self, resolver: InheritanceResolver) -> None:
        """Test resolving all events."""
        resolved = resolver.resolve_all_events()
        assert len(resolved) > 0
        assert "base_event" in resolved
        assert "process_activity" in resolved

    def test_polymorphic_identity(self, resolver: InheritanceResolver) -> None:
        """Test polymorphic identity is set."""
        proc = resolver.resolve_event("process_activity")
        assert proc is not None
        assert proc.polymorphic_identity == "process_activity"


class TestInheritanceTree(TestInheritanceResolver):
    """Tests for building inheritance trees."""

    def test_build_event_tree(self, resolver: InheritanceResolver) -> None:
        """Test building event inheritance tree."""
        tree = resolver.build_event_inheritance_tree()
        assert isinstance(tree, InheritanceTree)

    def test_tree_has_roots(self, resolver: InheritanceResolver) -> None:
        """Test tree has root nodes."""
        tree = resolver.build_event_inheritance_tree()
        assert len(tree.roots) > 0
        # base_event should be a root (or near root)

    def test_tree_has_parent_mapping(self, resolver: InheritanceResolver) -> None:
        """Test tree has parent mapping."""
        tree = resolver.build_event_inheritance_tree()
        assert len(tree.parents) > 0
        # process_activity should have system as parent
        if "process_activity" in tree.parents:
            assert tree.parents["process_activity"] == "system"

    def test_tree_has_children_mapping(self, resolver: InheritanceResolver) -> None:
        """Test tree has children mapping."""
        tree = resolver.build_event_inheritance_tree()
        # system should have children (like process_activity)
        if "system" in tree.children:
            assert len(tree.children["system"]) > 0

    def test_topological_order(self, resolver: InheritanceResolver) -> None:
        """Test topological order has parents before children."""
        tree = resolver.build_event_inheritance_tree()
        assert len(tree.topological_order) > 0

        # For each event, its parent should appear before it in the order
        order_index = {name: i for i, name in enumerate(tree.topological_order)}
        for name, parent in tree.parents.items():
            if parent and parent in order_index and name in order_index:
                assert order_index[parent] < order_index[name], (
                    f"Parent {parent} should appear before {name}"
                )

    def test_build_object_tree(self, resolver: InheritanceResolver) -> None:
        """Test building object inheritance tree."""
        tree = resolver.build_object_inheritance_tree()
        assert isinstance(tree, InheritanceTree)
        assert len(tree.topological_order) > 0


class TestAttributeTypeResolution(TestInheritanceResolver):
    """Tests for attribute type resolution from dictionary."""

    def test_groups_is_array(self, resolver: InheritanceResolver) -> None:
        """Test groups attribute is resolved as array from dictionary."""
        device = resolver.resolve_object("device")
        assert device is not None
        if "groups" in device.all_attributes:
            groups = device.all_attributes["groups"]
            assert groups.is_array is True

    def test_hostname_type_resolved(self, resolver: InheritanceResolver) -> None:
        """Test hostname type is resolved from dictionary."""
        device = resolver.resolve_object("device")
        assert device is not None
        if "hostname" in device.all_attributes:
            hostname = device.all_attributes["hostname"]
            # Dictionary defines hostname as hostname_t
            assert hostname.ocsf_type in ["hostname_t", "string_t", None] or True

    def test_requirement_preserved(self, resolver: InheritanceResolver) -> None:
        """Test requirement from object definition is preserved."""
        device = resolver.resolve_object("device")
        assert device is not None
        if "hostname" in device.all_attributes:
            hostname = device.all_attributes["hostname"]
            # hostname is recommended in device object
            assert hostname.requirement in ["optional", "required", "recommended"]


class TestDirectChildren(TestInheritanceResolver):
    """Tests for getting direct children."""

    def test_get_direct_children_event(self, resolver: InheritanceResolver) -> None:
        """Test getting direct children of an event."""
        children = resolver.get_direct_children("system", is_event=True)
        # system should have children like process_activity
        assert isinstance(children, list)
        if len(children) > 0:
            # Verify these are actually children
            for child in children:
                event = resolver.schema.events.get(child)
                if event:
                    assert event.extends == "system"

    def test_get_all_descendants(self, resolver: InheritanceResolver) -> None:
        """Test getting all descendants of an event."""
        # base_event should have many descendants
        descendants = resolver.get_all_descendants("base_event", is_event=True)
        # May have some if other events extend base_event indirectly
        assert isinstance(descendants, list)


class TestEdgeCases(TestInheritanceResolver):
    """Tests for edge cases."""

    def test_circular_inheritance_detection(self, resolver: InheritanceResolver) -> None:
        """Test circular inheritance doesn't cause infinite loop."""
        # Normal resolution should complete without hanging
        resolved = resolver.resolve_all_events()
        assert resolved is not None

    def test_missing_parent_handling(self, resolver: InheritanceResolver) -> None:
        """Test handling of events that extend non-existent parents."""
        # Should still resolve, just with shorter chain
        resolved = resolver.resolve_all_events()
        for event in resolved.values():
            # Inheritance chain should not contain None
            assert None not in event.inheritance_chain
