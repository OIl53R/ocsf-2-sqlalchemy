"""OCSF Inheritance Resolver.

Resolves inheritance chains (extends) for OCSF objects and events,
and determines SQLAlchemy joined table inheritance structure.
"""

from dataclasses import dataclass, field
from typing import Any

from .schema_loader import OcsfSchema, OcsfObject, OcsfEvent, OcsfAttribute


@dataclass
class ResolvedAttribute:
    """An attribute with resolved type and inheritance info."""

    name: str
    caption: str
    description: str
    ocsf_type: str | None = None
    requirement: str = "optional"
    is_array: bool = False
    is_inherited: bool = False
    source_object: str | None = None  # Where this attribute was defined
    enum: dict | None = None
    observable: int | None = None
    object_type: str | None = None  # For object references


@dataclass
class ResolvedObject:
    """An object with fully resolved inheritance."""

    name: str
    caption: str
    description: str
    extends: str | None = None
    inheritance_chain: list[str] = field(default_factory=list)
    own_attributes: dict[str, ResolvedAttribute] = field(default_factory=dict)
    inherited_attributes: dict[str, ResolvedAttribute] = field(default_factory=dict)
    all_attributes: dict[str, ResolvedAttribute] = field(default_factory=dict)


@dataclass
class ResolvedEvent:
    """An event with fully resolved inheritance."""

    name: str
    caption: str
    description: str
    uid: int
    category: str
    extends: str | None = None
    inheritance_chain: list[str] = field(default_factory=list)
    own_attributes: dict[str, ResolvedAttribute] = field(default_factory=dict)
    inherited_attributes: dict[str, ResolvedAttribute] = field(default_factory=dict)
    all_attributes: dict[str, ResolvedAttribute] = field(default_factory=dict)
    polymorphic_identity: str = ""


@dataclass
class InheritanceTree:
    """Represents the inheritance hierarchy for code generation."""

    # Map of parent -> list of children
    children: dict[str, list[str]] = field(default_factory=dict)
    # Map of child -> parent
    parents: dict[str, str | None] = field(default_factory=dict)
    # Root nodes (no parent)
    roots: list[str] = field(default_factory=list)
    # All nodes in topological order (parents before children)
    topological_order: list[str] = field(default_factory=list)


class InheritanceResolver:
    """Resolves OCSF inheritance chains for objects and events.

    OCSF uses an `extends` field to indicate inheritance. This resolver:
    1. Builds complete inheritance chains
    2. Merges attributes from parent to child
    3. Identifies which attributes are inherited vs. own
    4. Prepares SQLAlchemy joined table inheritance metadata
    """

    def __init__(self, schema: OcsfSchema) -> None:
        """Initialize with a loaded OCSF schema.

        Args:
            schema: The loaded OcsfSchema
        """
        self.schema = schema
        self._dictionary_attrs = schema.dictionary.get("attributes", {})

    def resolve_object(self, name: str) -> ResolvedObject | None:
        """Resolve inheritance for a single object.

        Args:
            name: Object name

        Returns:
            ResolvedObject with all inheritance resolved, or None if not found
        """
        obj = self.schema.objects.get(name)
        if obj is None:
            return None

        # Build inheritance chain (child -> ... -> root)
        chain = self._build_inheritance_chain_object(name)

        # Collect inherited attributes (from parent to child order)
        inherited = {}
        for parent_name in reversed(chain[1:]):  # Skip self, start from root
            parent = self.schema.objects.get(parent_name)
            if parent:
                for attr_name, attr in parent.attributes.items():
                    resolved = self._resolve_attribute(attr, parent_name)
                    resolved.is_inherited = True
                    inherited[attr_name] = resolved

        # Collect own attributes (can override inherited)
        own = {}
        for attr_name, attr in obj.attributes.items():
            resolved = self._resolve_attribute(attr, name)
            resolved.is_inherited = False
            own[attr_name] = resolved

        # Merge all attributes (own overrides inherited)
        all_attrs = {**inherited, **own}

        return ResolvedObject(
            name=name,
            caption=obj.caption,
            description=obj.description,
            extends=obj.extends,
            inheritance_chain=chain,
            own_attributes=own,
            inherited_attributes=inherited,
            all_attributes=all_attrs,
        )

    def resolve_event(self, name: str) -> ResolvedEvent | None:
        """Resolve inheritance for a single event.

        Args:
            name: Event name

        Returns:
            ResolvedEvent with all inheritance resolved, or None if not found
        """
        event = self.schema.events.get(name)
        if event is None:
            return None

        # Build inheritance chain
        chain = self._build_inheritance_chain_event(name)

        # Collect inherited attributes
        inherited = {}
        for parent_name in reversed(chain[1:]):  # Skip self
            parent = self.schema.events.get(parent_name)
            if parent:
                for attr_name, attr in parent.attributes.items():
                    resolved = self._resolve_attribute(attr, parent_name)
                    resolved.is_inherited = True
                    inherited[attr_name] = resolved

        # Collect own attributes
        own = {}
        for attr_name, attr in event.attributes.items():
            resolved = self._resolve_attribute(attr, name)
            resolved.is_inherited = False
            own[attr_name] = resolved

        # Merge all attributes
        all_attrs = {**inherited, **own}

        # Generate polymorphic identity (snake_case of event name)
        polymorphic_id = name.lower().replace(" ", "_")

        return ResolvedEvent(
            name=name,
            caption=event.caption,
            description=event.description,
            uid=event.uid,
            category=event.category,
            extends=event.extends,
            inheritance_chain=chain,
            own_attributes=own,
            inherited_attributes=inherited,
            all_attributes=all_attrs,
            polymorphic_identity=polymorphic_id,
        )

    def resolve_all_objects(self) -> dict[str, ResolvedObject]:
        """Resolve inheritance for all objects.

        Returns:
            Dictionary of object name -> ResolvedObject
        """
        resolved = {}
        for name in self.schema.objects:
            obj = self.resolve_object(name)
            if obj:
                resolved[name] = obj
        return resolved

    def resolve_all_events(self) -> dict[str, ResolvedEvent]:
        """Resolve inheritance for all events.

        Returns:
            Dictionary of event name -> ResolvedEvent
        """
        resolved = {}
        for name in self.schema.events:
            event = self.resolve_event(name)
            if event:
                resolved[name] = event
        return resolved

    def build_event_inheritance_tree(self) -> InheritanceTree:
        """Build the inheritance tree for events.

        Returns:
            InheritanceTree with parent/child relationships
        """
        tree = InheritanceTree()

        # Build parent/child maps
        for name, event in self.schema.events.items():
            parent = event.extends
            tree.parents[name] = parent

            if parent:
                if parent not in tree.children:
                    tree.children[parent] = []
                tree.children[parent].append(name)
            else:
                tree.roots.append(name)

        # Build topological order (parents before children)
        tree.topological_order = self._topological_sort_events()

        return tree

    def build_object_inheritance_tree(self) -> InheritanceTree:
        """Build the inheritance tree for objects.

        Returns:
            InheritanceTree with parent/child relationships
        """
        tree = InheritanceTree()

        for name, obj in self.schema.objects.items():
            parent = obj.extends
            tree.parents[name] = parent

            if parent:
                if parent not in tree.children:
                    tree.children[parent] = []
                tree.children[parent].append(name)
            else:
                tree.roots.append(name)

        tree.topological_order = self._topological_sort_objects()

        return tree

    def _build_inheritance_chain_object(self, name: str) -> list[str]:
        """Build inheritance chain for an object (child -> parent -> root).

        Args:
            name: Starting object name

        Returns:
            List of names from child to root
        """
        chain = [name]
        current = self.schema.objects.get(name)

        while current and current.extends:
            parent_name = current.extends
            if parent_name in chain:
                # Circular inheritance - break to avoid infinite loop
                break
            chain.append(parent_name)
            current = self.schema.objects.get(parent_name)

        return chain

    def _build_inheritance_chain_event(self, name: str) -> list[str]:
        """Build inheritance chain for an event (child -> parent -> root).

        Args:
            name: Starting event name

        Returns:
            List of names from child to root
        """
        chain = [name]
        current = self.schema.events.get(name)

        while current and current.extends:
            parent_name = current.extends
            if parent_name in chain:
                # Circular inheritance - break to avoid infinite loop
                break
            chain.append(parent_name)
            current = self.schema.events.get(parent_name)

        return chain

    def _resolve_attribute(
        self, attr: OcsfAttribute, source: str
    ) -> ResolvedAttribute:
        """Resolve attribute type from dictionary.

        Args:
            attr: The attribute to resolve
            source: The object/event where this attribute is defined

        Returns:
            ResolvedAttribute with type info from dictionary
        """
        # Look up attribute definition in dictionary
        dict_attr = self._dictionary_attrs.get(attr.name, {})

        # Get type from attribute or dictionary
        ocsf_type = attr.type or dict_attr.get("type")

        # Get is_array from attribute or dictionary
        is_array = attr.is_array or dict_attr.get("is_array", False)

        # Get caption from attribute or dictionary
        caption = attr.caption if attr.caption != attr.name else dict_attr.get("caption", attr.name)

        return ResolvedAttribute(
            name=attr.name,
            caption=caption,
            description=attr.description or dict_attr.get("description", ""),
            ocsf_type=ocsf_type,
            requirement=attr.requirement,
            is_array=is_array,
            is_inherited=False,
            source_object=source,
            enum=attr.enum or dict_attr.get("enum"),
            observable=attr.observable or dict_attr.get("observable"),
            object_type=attr.object_type or dict_attr.get("object_type"),
        )

    def _topological_sort_events(self) -> list[str]:
        """Sort events in topological order (parents before children).

        Returns:
            List of event names in order
        """
        # Kahn's algorithm
        in_degree = {name: 0 for name in self.schema.events}
        adj = {name: [] for name in self.schema.events}

        for name, event in self.schema.events.items():
            if event.extends and event.extends in self.schema.events:
                adj[event.extends].append(name)
                in_degree[name] += 1

        # Start with nodes that have no parents
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for child in adj.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return result

    def _topological_sort_objects(self) -> list[str]:
        """Sort objects in topological order (parents before children).

        Returns:
            List of object names in order
        """
        in_degree = {name: 0 for name in self.schema.objects}
        adj = {name: [] for name in self.schema.objects}

        for name, obj in self.schema.objects.items():
            if obj.extends and obj.extends in self.schema.objects:
                adj[obj.extends].append(name)
                in_degree[name] += 1

        queue = [name for name, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for child in adj.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return result

    def get_direct_children(self, name: str, is_event: bool = True) -> list[str]:
        """Get direct children of an object or event.

        Args:
            name: Parent name
            is_event: True for events, False for objects

        Returns:
            List of direct child names
        """
        items = self.schema.events if is_event else self.schema.objects
        children = []

        for item_name, item in items.items():
            if item.extends == name:
                children.append(item_name)

        return children

    def get_all_descendants(self, name: str, is_event: bool = True) -> list[str]:
        """Get all descendants of an object or event (recursive).

        Args:
            name: Ancestor name
            is_event: True for events, False for objects

        Returns:
            List of all descendant names
        """
        descendants = []
        to_process = self.get_direct_children(name, is_event)

        while to_process:
            child = to_process.pop(0)
            descendants.append(child)
            to_process.extend(self.get_direct_children(child, is_event))

        return descendants
