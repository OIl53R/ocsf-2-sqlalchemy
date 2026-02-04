"""OCSF Object Filter for Partial Schema Generation.

Filters analyzed schema to include only objects reachable from a core object
within a specified depth, while preserving inheritance chains required for
SQLAlchemy joined-table inheritance.
"""

from collections import deque
from dataclasses import dataclass, field

from .schema_analyzer import AnalyzedSchema, ArrayAttributeInfo, RelationshipInfo
from .inheritance_resolver import InheritanceTree, ResolvedObject


@dataclass
class FilterConfig:
    """Configuration for object filtering."""

    core_object: str
    max_depth: int = 3
    include_events: bool = False


@dataclass
class FilterResult:
    """Results and metadata from filtering operation."""

    included_objects: set[str] = field(default_factory=set)
    object_depths: dict[str, int] = field(default_factory=dict)
    inheritance_additions: set[str] = field(default_factory=set)
    excluded_objects: set[str] = field(default_factory=set)
    included_events: set[str] = field(default_factory=set)


class ObjectFilter:
    """Filters AnalyzedSchema to include only objects reachable from a core object.

    Uses BFS traversal to find all objects within max_depth relationship hops,
    then ensures all required inheritance parent classes are included for
    SQLAlchemy joined-table inheritance.
    """

    def __init__(self, analyzed: AnalyzedSchema) -> None:
        """Initialize with an analyzed schema.

        Args:
            analyzed: The complete analyzed schema to filter
        """
        self.analyzed = analyzed

    def filter(self, config: FilterConfig) -> tuple[AnalyzedSchema, FilterResult]:
        """Filter schema to include only objects reachable from core object.

        Args:
            config: Filter configuration with core object and max depth

        Returns:
            Tuple of (filtered AnalyzedSchema, FilterResult with metadata)

        Raises:
            ValueError: If core_object doesn't exist in schema
        """
        if config.core_object not in self.analyzed.objects:
            available = sorted(self.analyzed.objects.keys())[:10]
            raise ValueError(
                f"Core object '{config.core_object}' not found in schema. "
                f"Available objects include: {', '.join(available)}..."
            )

        # BFS traversal to find reachable objects
        included, depths = self._bfs_traverse(config.core_object, config.max_depth)

        # Add inheritance parents (required for SQLAlchemy joined-table inheritance)
        inheritance_additions = self._add_inheritance_parents(included)
        all_included = included | inheritance_additions

        # Determine excluded objects
        excluded = set(self.analyzed.objects.keys()) - all_included

        # Find events if requested
        included_events: set[str] = set()
        if config.include_events:
            included_events = self._find_related_events(all_included)

        # Build filtered schema
        filtered = self._build_filtered_schema(all_included, included_events)

        result = FilterResult(
            included_objects=included,
            object_depths=depths,
            inheritance_additions=inheritance_additions,
            excluded_objects=excluded,
            included_events=included_events,
        )

        return filtered, result

    def _bfs_traverse(
        self, core: str, max_depth: int
    ) -> tuple[set[str], dict[str, int]]:
        """BFS traversal from core object, tracking depth.

        Args:
            core: Starting object name
            max_depth: Maximum relationship depth to traverse

        Returns:
            Tuple of (set of included object names, dict of object -> depth)
        """
        included: set[str] = set()
        depths: dict[str, int] = {}
        queue: deque[tuple[str, int]] = deque([(core, 0)])

        while queue:
            obj_name, depth = queue.popleft()

            # Skip if already visited (handles circular references)
            if obj_name in included:
                continue

            # Skip if not a valid object in schema
            if obj_name not in self.analyzed.objects:
                continue

            included.add(obj_name)
            depths[obj_name] = depth

            # Don't traverse beyond max_depth
            if depth >= max_depth:
                continue

            # Get dependencies and add to queue
            deps = self._get_object_dependencies(obj_name)
            for dep in deps:
                if dep not in included:
                    queue.append((dep, depth + 1))

        return included, depths

    def _get_object_dependencies(self, obj_name: str) -> set[str]:
        """Get objects referenced by the given object.

        Checks both explicit object_type references and ocsf_type values
        that correspond to object names in the schema.

        Args:
            obj_name: Object name to get dependencies for

        Returns:
            Set of object names that this object references
        """
        deps: set[str] = set()
        obj = self.analyzed.objects.get(obj_name)

        if not obj:
            return deps

        for attr in obj.all_attributes.values():
            # Direct object reference via object_type
            if attr.object_type:
                deps.add(attr.object_type)
            # Check if ocsf_type refers to an object (not a primitive like string_t)
            elif attr.ocsf_type and attr.ocsf_type in self.analyzed.objects:
                deps.add(attr.ocsf_type)

        return deps

    def _add_inheritance_parents(self, included: set[str]) -> set[str]:
        """Add missing parent classes required for inheritance chains.

        SQLAlchemy joined-table inheritance requires all parent classes to exist.
        This adds any missing parents from inheritance chains.

        Args:
            included: Set of objects already included

        Returns:
            Set of additional parent objects that were added
        """
        additions: set[str] = set()

        for obj_name in list(included):
            obj = self.analyzed.objects.get(obj_name)
            if not obj:
                continue

            # Walk inheritance chain and add missing parents
            for parent_name in obj.inheritance_chain[1:]:  # Skip self
                if parent_name not in included and parent_name in self.analyzed.objects:
                    additions.add(parent_name)

        return additions

    def _find_related_events(self, included_objects: set[str]) -> set[str]:
        """Find events that reference any of the included objects.

        Args:
            included_objects: Set of included object names

        Returns:
            Set of event names that reference included objects
        """
        related_events: set[str] = set()

        for event_name, event in self.analyzed.events.items():
            # Check if any attribute references an included object
            for attr in event.all_attributes.values():
                if attr.object_type and attr.object_type in included_objects:
                    related_events.add(event_name)
                    break

        return related_events

    def _build_filtered_schema(
        self, included_objects: set[str], included_events: set[str]
    ) -> AnalyzedSchema:
        """Build a new AnalyzedSchema with only included objects.

        Args:
            included_objects: Set of object names to include
            included_events: Set of event names to include

        Returns:
            New AnalyzedSchema with filtered content
        """
        # Filter objects
        filtered_objects = {
            name: obj
            for name, obj in self.analyzed.objects.items()
            if name in included_objects
        }

        # Filter events
        filtered_events = {
            name: event
            for name, event in self.analyzed.events.items()
            if name in included_events
        }

        # Rebuild inheritance trees
        object_tree = self._rebuild_inheritance_tree(included_objects)
        event_tree = self._rebuild_event_tree(included_events)

        # Filter relationships (only if both source and target are included)
        filtered_relationships = self._filter_relationships(
            included_objects, included_events
        )

        # Filter array attributes (only if parent is included)
        filtered_arrays = self._filter_array_attributes(
            included_objects, included_events
        )

        # Filter enums (include all for now - they're lightweight)
        filtered_enums = self.analyzed.enums

        return AnalyzedSchema(
            version=self.analyzed.version,
            objects=filtered_objects,
            events=filtered_events,
            object_tree=object_tree,
            event_tree=event_tree,
            relationships=filtered_relationships,
            array_attributes=filtered_arrays,
            enums=filtered_enums,
            categories=self.analyzed.categories,
        )

    def _rebuild_inheritance_tree(self, included: set[str]) -> InheritanceTree:
        """Rebuild inheritance tree with only included objects.

        Args:
            included: Set of included object names

        Returns:
            New InheritanceTree for filtered objects
        """
        tree = InheritanceTree()
        original = self.analyzed.object_tree

        for obj_name in included:
            original_parent = original.parents.get(obj_name)

            # Only include parent if it's in our filtered set
            if original_parent and original_parent in included:
                tree.parents[obj_name] = original_parent
                if original_parent not in tree.children:
                    tree.children[original_parent] = []
                tree.children[original_parent].append(obj_name)
            else:
                tree.parents[obj_name] = None
                tree.roots.append(obj_name)

        # Rebuild topological order using Kahn's algorithm
        tree.topological_order = self._topological_sort(tree, included)

        return tree

    def _rebuild_event_tree(self, included: set[str]) -> InheritanceTree:
        """Rebuild inheritance tree with only included events.

        Args:
            included: Set of included event names

        Returns:
            New InheritanceTree for filtered events
        """
        if not included:
            return InheritanceTree()

        tree = InheritanceTree()
        original = self.analyzed.event_tree

        for event_name in included:
            original_parent = original.parents.get(event_name)

            if original_parent and original_parent in included:
                tree.parents[event_name] = original_parent
                if original_parent not in tree.children:
                    tree.children[original_parent] = []
                tree.children[original_parent].append(event_name)
            else:
                tree.parents[event_name] = None
                tree.roots.append(event_name)

        tree.topological_order = self._topological_sort(tree, included)

        return tree

    def _topological_sort(self, tree: InheritanceTree, included: set[str]) -> list[str]:
        """Topological sort for inheritance tree (parents before children).

        Args:
            tree: The inheritance tree to sort
            included: Set of included names

        Returns:
            List of names in topological order
        """
        in_degree = {name: 0 for name in included}
        adj: dict[str, list[str]] = {name: [] for name in included}

        for name in included:
            parent = tree.parents.get(name)
            if parent and parent in included:
                adj[parent].append(name)
                in_degree[name] += 1

        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            for child in adj.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return result

    def _filter_relationships(
        self, included_objects: set[str], included_events: set[str]
    ) -> list[RelationshipInfo]:
        """Filter relationships to only include those between included entities.

        Args:
            included_objects: Set of included object names
            included_events: Set of included event names

        Returns:
            Filtered list of RelationshipInfo
        """
        all_included = included_objects | included_events
        filtered = []

        for rel in self.analyzed.relationships:
            source_included = rel.source_entity in all_included
            target_included = rel.target_entity in included_objects

            if source_included and target_included:
                filtered.append(rel)

        return filtered

    def _filter_array_attributes(
        self, included_objects: set[str], included_events: set[str]
    ) -> list[ArrayAttributeInfo]:
        """Filter array attributes to only include those from included entities.

        For object arrays, only include if both parent and element type are included.
        For primitive arrays, include if parent is included.

        Args:
            included_objects: Set of included object names
            included_events: Set of included event names

        Returns:
            Filtered list of ArrayAttributeInfo
        """
        all_included = included_objects | included_events
        filtered = []

        for arr in self.analyzed.array_attributes:
            # Parent must be included
            if arr.parent_entity not in all_included:
                continue

            # For primitive arrays, just need parent to be included
            if arr.is_primitive:
                filtered.append(arr)
                continue

            # For object arrays, element type must also be included
            if arr.element_type in included_objects:
                filtered.append(arr)

        return filtered
