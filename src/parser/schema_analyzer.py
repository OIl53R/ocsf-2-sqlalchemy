"""OCSF Schema Analyzer.

Orchestrates schema loading, inheritance resolution, and relationship analysis.
Provides the complete analyzed schema ready for code generation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .schema_loader import SchemaLoader, OcsfSchema
from .inheritance_resolver import (
    InheritanceResolver,
    ResolvedObject,
    ResolvedEvent,
    ResolvedAttribute,
    InheritanceTree,
)
from .type_mapper import TypeMapper


@dataclass
class RelationshipInfo:
    """Information about a relationship between entities."""

    source_entity: str  # The entity that has this attribute
    attribute_name: str  # The attribute name
    target_entity: str  # The referenced entity (object type)
    is_array: bool  # Whether this is a one-to-many/many-to-many
    is_nullable: bool  # Whether the relationship is optional
    relationship_type: str  # "foreign_key", "association_table"


@dataclass
class ArrayAttributeInfo:
    """Information about an array attribute requiring an association table."""

    parent_entity: str  # The entity containing this array
    attribute_name: str  # The array attribute name
    element_type: str  # The type of elements in the array
    is_primitive: bool  # True if elements are primitives, False if objects
    association_table_name: str  # Generated name for the association table


@dataclass
class EnumInfo:
    """Information about an enum type."""

    name: str  # Enum name
    values: dict[int, str]  # ID -> caption mapping
    description: str = ""


@dataclass
class AnalyzedSchema:
    """Complete analyzed schema ready for code generation."""

    version: str
    objects: dict[str, ResolvedObject]
    events: dict[str, ResolvedEvent]
    object_tree: InheritanceTree
    event_tree: InheritanceTree
    relationships: list[RelationshipInfo]
    array_attributes: list[ArrayAttributeInfo]
    enums: dict[str, EnumInfo]
    categories: dict[str, Any]


class SchemaAnalyzer:
    """Analyzes OCSF schema and prepares it for code generation.

    Combines:
    - Schema loading
    - Inheritance resolution
    - Relationship analysis (foreign keys, associations)
    - Type mapping
    - Enum extraction
    """

    def __init__(
        self,
        schema_path: Path | str,
        type_mapper: TypeMapper | None = None,
    ) -> None:
        """Initialize the analyzer.

        Args:
            schema_path: Path to the ocsf-schema repository
            type_mapper: Optional custom type mapper
        """
        self.schema_path = Path(schema_path)
        self.type_mapper = type_mapper or TypeMapper()
        self._loader: SchemaLoader | None = None
        self._schema: OcsfSchema | None = None
        self._resolver: InheritanceResolver | None = None

    @property
    def loader(self) -> SchemaLoader:
        """Get or create the schema loader."""
        if self._loader is None:
            self._loader = SchemaLoader(self.schema_path)
        return self._loader

    @property
    def schema(self) -> OcsfSchema:
        """Get or load the raw schema."""
        if self._schema is None:
            self._schema = self.loader.load()
        return self._schema

    @property
    def resolver(self) -> InheritanceResolver:
        """Get or create the inheritance resolver."""
        if self._resolver is None:
            self._resolver = InheritanceResolver(self.schema)
        return self._resolver

    def analyze(self) -> AnalyzedSchema:
        """Perform complete schema analysis.

        Returns:
            AnalyzedSchema ready for code generation
        """
        # Resolve all objects and events
        objects = self.resolver.resolve_all_objects()
        events = self.resolver.resolve_all_events()

        # Build inheritance trees
        object_tree = self.resolver.build_object_inheritance_tree()
        event_tree = self.resolver.build_event_inheritance_tree()

        # Analyze relationships
        relationships = self._analyze_relationships(objects, events)

        # Find array attributes
        array_attributes = self._find_array_attributes(objects, events)

        # Extract enums
        enums = self._extract_enums(objects, events)

        return AnalyzedSchema(
            version=self.schema.version,
            objects=objects,
            events=events,
            object_tree=object_tree,
            event_tree=event_tree,
            relationships=relationships,
            array_attributes=array_attributes,
            enums=enums,
            categories=self.schema.categories,
        )

    def _analyze_relationships(
        self,
        objects: dict[str, ResolvedObject],
        events: dict[str, ResolvedEvent],
    ) -> list[RelationshipInfo]:
        """Analyze all object/event references to identify relationships.

        Args:
            objects: Resolved objects
            events: Resolved events

        Returns:
            List of RelationshipInfo for all FK/association relationships
        """
        relationships = []

        # Analyze object relationships
        for obj_name, obj in objects.items():
            for attr_name, attr in obj.all_attributes.items():
                rel = self._analyze_attribute_relationship(obj_name, attr)
                if rel:
                    relationships.append(rel)

        # Analyze event relationships
        for event_name, event in events.items():
            for attr_name, attr in event.all_attributes.items():
                rel = self._analyze_attribute_relationship(event_name, attr)
                if rel:
                    relationships.append(rel)

        return relationships

    def _analyze_attribute_relationship(
        self, entity_name: str, attr: ResolvedAttribute
    ) -> RelationshipInfo | None:
        """Analyze a single attribute for object relationships.

        Args:
            entity_name: The containing entity name
            attr: The attribute to analyze

        Returns:
            RelationshipInfo if this is an object reference, None otherwise
        """
        # Check if this is an object type (not a primitive)
        if attr.object_type:
            target = attr.object_type
        elif attr.ocsf_type and self.type_mapper.is_object_type(attr.ocsf_type):
            target = attr.ocsf_type
        else:
            return None

        is_nullable = attr.requirement != "required"
        relationship_type = "association_table" if attr.is_array else "foreign_key"

        return RelationshipInfo(
            source_entity=entity_name,
            attribute_name=attr.name,
            target_entity=target,
            is_array=attr.is_array,
            is_nullable=is_nullable,
            relationship_type=relationship_type,
        )

    def _find_array_attributes(
        self,
        objects: dict[str, ResolvedObject],
        events: dict[str, ResolvedEvent],
    ) -> list[ArrayAttributeInfo]:
        """Find all array attributes that need association tables.

        Args:
            objects: Resolved objects
            events: Resolved events

        Returns:
            List of ArrayAttributeInfo for all array attributes
        """
        arrays = []

        # Process objects
        for obj_name, obj in objects.items():
            for attr_name, attr in obj.all_attributes.items():
                if attr.is_array:
                    array_info = self._create_array_info(obj_name, attr)
                    arrays.append(array_info)

        # Process events
        for event_name, event in events.items():
            for attr_name, attr in event.all_attributes.items():
                if attr.is_array:
                    array_info = self._create_array_info(event_name, attr)
                    arrays.append(array_info)

        return arrays

    def _create_array_info(
        self, parent_name: str, attr: ResolvedAttribute
    ) -> ArrayAttributeInfo:
        """Create ArrayAttributeInfo for an array attribute.

        Args:
            parent_name: The containing entity name
            attr: The array attribute

        Returns:
            ArrayAttributeInfo
        """
        # Determine element type
        element_type = attr.object_type or attr.ocsf_type or "string_t"

        # Check if primitive
        is_primitive = not self.type_mapper.is_object_type(element_type)

        # Generate association table name
        from .naming import NamingConvention
        naming = NamingConvention()
        table_name = naming.association_table_name(parent_name, attr.name)

        return ArrayAttributeInfo(
            parent_entity=parent_name,
            attribute_name=attr.name,
            element_type=element_type,
            is_primitive=is_primitive,
            association_table_name=table_name,
        )

    def _extract_enums(
        self,
        objects: dict[str, ResolvedObject],
        events: dict[str, ResolvedEvent],
    ) -> dict[str, EnumInfo]:
        """Extract all enum definitions from schema.

        Args:
            objects: Resolved objects
            events: Resolved events

        Returns:
            Dictionary of enum name -> EnumInfo
        """
        enums = {}

        # Extract from objects
        for obj in objects.values():
            for attr in obj.all_attributes.values():
                if attr.enum:
                    enum_name = f"{attr.name}_enum"
                    if enum_name not in enums:
                        enums[enum_name] = self._parse_enum(enum_name, attr.enum)

        # Extract from events
        for event in events.values():
            for attr in event.all_attributes.values():
                if attr.enum:
                    enum_name = f"{attr.name}_enum"
                    if enum_name not in enums:
                        enums[enum_name] = self._parse_enum(enum_name, attr.enum)

        # Also extract from dictionary
        dict_attrs = self.schema.dictionary.get("attributes", {})
        for attr_name, attr_data in dict_attrs.items():
            if isinstance(attr_data, dict) and attr_data.get("enum"):
                enum_name = f"{attr_name}_enum"
                if enum_name not in enums:
                    enums[enum_name] = self._parse_enum(enum_name, attr_data["enum"])

        return enums

    def _parse_enum(self, name: str, enum_data: dict) -> EnumInfo:
        """Parse an enum definition.

        Args:
            name: Enum name
            enum_data: Raw enum data from schema

        Returns:
            EnumInfo
        """
        values = {}
        description = enum_data.get("description", "")

        # Enum values are typically in a nested structure
        for key, val in enum_data.items():
            if key in ("description", "caption", "type"):
                continue
            if isinstance(val, dict):
                # Value with caption
                try:
                    int_key = int(key)
                    values[int_key] = val.get("caption", str(key))
                except ValueError:
                    pass
            elif isinstance(val, (int, str)):
                # Simple value
                try:
                    int_key = int(key)
                    values[int_key] = str(val)
                except ValueError:
                    pass

        return EnumInfo(name=name, values=values, description=description)

    def get_object_dependencies(self, object_name: str) -> list[str]:
        """Get list of objects that this object depends on (references).

        Args:
            object_name: Object name

        Returns:
            List of object names that this object references
        """
        deps = set()
        obj = self.resolver.resolve_object(object_name)

        if obj:
            for attr in obj.all_attributes.values():
                if attr.object_type:
                    deps.add(attr.object_type)
                elif attr.ocsf_type and self.type_mapper.is_object_type(attr.ocsf_type):
                    deps.add(attr.ocsf_type)

        return list(deps)

    def get_generation_order(self) -> tuple[list[str], list[str]]:
        """Get the order for generating objects and events.

        Returns objects and events in dependency order (parents/dependencies first).

        Returns:
            Tuple of (object_names, event_names) in generation order
        """
        object_tree = self.resolver.build_object_inheritance_tree()
        event_tree = self.resolver.build_event_inheritance_tree()

        return (object_tree.topological_order, event_tree.topological_order)

    def get_entity_columns(self, entity_name: str, is_event: bool = False) -> list[dict]:
        """Get column definitions for an entity.

        Args:
            entity_name: Object or event name
            is_event: True for events, False for objects

        Returns:
            List of column info dicts with name, type, nullable, etc.
        """
        columns = []

        if is_event:
            entity = self.resolver.resolve_event(entity_name)
        else:
            entity = self.resolver.resolve_object(entity_name)

        if not entity:
            return columns

        for attr in entity.own_attributes.values():
            # Skip array attributes (they become association tables)
            if attr.is_array:
                continue

            # Skip object references (they become foreign keys)
            if attr.object_type or self.type_mapper.is_object_type(attr.ocsf_type or ""):
                # Add FK column instead
                columns.append({
                    "name": f"{attr.name}_id",
                    "type": "Integer",
                    "nullable": attr.requirement != "required",
                    "is_foreign_key": True,
                    "references": attr.object_type or attr.ocsf_type,
                })
                continue

            # Get SQLAlchemy type
            sa_type = self.type_mapper.get_sqlalchemy_type(attr.ocsf_type or "string_t")

            columns.append({
                "name": attr.name,
                "type": sa_type,
                "nullable": attr.requirement != "required",
                "is_foreign_key": False,
                "description": attr.description,
            })

        return columns
