"""OCSF Schema Loader.

Loads and parses OCSF schema from local filesystem (cloned repository).
Provides access to objects, events, categories, and attribute definitions.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class OcsfAttribute:
    """Represents an OCSF attribute definition."""

    name: str
    caption: str
    description: str
    type: str | None = None
    requirement: str = "optional"
    is_array: bool = False
    deprecated: dict | None = None
    enum: dict | None = None
    group: str | None = None
    observable: int | None = None
    profile: str | None = None
    sibling: str | None = None
    object_type: str | None = None
    object_name: str | None = None


@dataclass
class OcsfObject:
    """Represents an OCSF object definition."""

    name: str
    caption: str
    description: str
    extends: str | None = None
    attributes: dict[str, OcsfAttribute] = field(default_factory=dict)
    constraints: dict | None = None
    observable: int | None = None
    profiles: list[str] = field(default_factory=list)


@dataclass
class OcsfEvent:
    """Represents an OCSF event class definition."""

    name: str
    caption: str
    description: str
    uid: int
    category: str
    extends: str | None = None
    attributes: dict[str, OcsfAttribute] = field(default_factory=dict)
    profiles: list[str] = field(default_factory=list)
    constraints: dict | None = None


@dataclass
class OcsfCategory:
    """Represents an OCSF category definition."""

    name: str
    caption: str
    description: str
    uid: int
    classes: list[str] = field(default_factory=list)


@dataclass
class OcsfSchema:
    """Complete OCSF schema representation."""

    version: str
    objects: dict[str, OcsfObject] = field(default_factory=dict)
    events: dict[str, OcsfEvent] = field(default_factory=dict)
    categories: dict[str, OcsfCategory] = field(default_factory=dict)
    dictionary: dict[str, Any] = field(default_factory=dict)
    types: dict[str, Any] = field(default_factory=dict)


class SchemaLoader:
    """Loads OCSF schema from a local repository.

    Parses the raw JSON files from the ocsf-schema repository to build
    a complete schema representation with resolved inheritance.
    """

    def __init__(self, schema_path: Path | str) -> None:
        """Initialize the schema loader.

        Args:
            schema_path: Path to the ocsf-schema repository root
        """
        self.schema_path = Path(schema_path)
        self._validate_path()

    def _validate_path(self) -> None:
        """Validate that the schema path exists and contains expected files."""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema path does not exist: {self.schema_path}")

        required_files = ["version.json", "dictionary.json", "categories.json"]
        for filename in required_files:
            if not (self.schema_path / filename).exists():
                raise FileNotFoundError(
                    f"Required file not found: {self.schema_path / filename}"
                )

    def _load_json(self, path: Path) -> dict:
        """Load and parse a JSON file.

        Args:
            path: Path to the JSON file

        Returns:
            Parsed JSON as dictionary
        """
        return json.loads(path.read_text(encoding="utf-8"))

    def load(self) -> OcsfSchema:
        """Load the complete OCSF schema.

        Returns:
            OcsfSchema with all objects, events, categories loaded
        """
        # Load version
        version_data = self._load_json(self.schema_path / "version.json")
        version = version_data.get("version", "unknown")

        # Load dictionary (attribute definitions and types)
        dictionary = self._load_json(self.schema_path / "dictionary.json")

        # Load types from dictionary
        types = self._load_types(dictionary)

        # Load categories
        categories = self._load_categories()

        # Load objects
        objects = self._load_objects()

        # Load events
        events = self._load_events(categories)

        return OcsfSchema(
            version=version,
            objects=objects,
            events=events,
            categories=categories,
            dictionary=dictionary,
            types=types,
        )

    def _load_types(self, dictionary: dict) -> dict[str, Any]:
        """Extract type definitions from dictionary.

        Args:
            dictionary: The loaded dictionary.json

        Returns:
            Dictionary of type definitions
        """
        types_data = dictionary.get("types", {})
        attributes = types_data.get("attributes", {})
        return attributes

    def _load_categories(self) -> dict[str, OcsfCategory]:
        """Load category definitions.

        Returns:
            Dictionary of category name -> OcsfCategory
        """
        categories_data = self._load_json(self.schema_path / "categories.json")
        categories = {}

        for name, cat_data in categories_data.get("attributes", {}).items():
            categories[name] = OcsfCategory(
                name=name,
                caption=cat_data.get("caption", name),
                description=cat_data.get("description", ""),
                uid=cat_data.get("uid", 0),
                classes=cat_data.get("classes", []),
            )

        return categories

    def _load_objects(self) -> dict[str, OcsfObject]:
        """Load all object definitions from objects/ directory.

        Returns:
            Dictionary of object name -> OcsfObject
        """
        objects = {}
        objects_dir = self.schema_path / "objects"

        if not objects_dir.exists():
            return objects

        for obj_file in objects_dir.glob("*.json"):
            try:
                obj_data = self._load_json(obj_file)
                obj_name = obj_file.stem

                # Parse attributes
                attributes = self._parse_attributes(obj_data.get("attributes", {}))

                objects[obj_name] = OcsfObject(
                    name=obj_name,
                    caption=obj_data.get("caption", obj_name),
                    description=obj_data.get("description", ""),
                    extends=obj_data.get("extends"),
                    attributes=attributes,
                    constraints=obj_data.get("constraints"),
                    observable=obj_data.get("observable"),
                    profiles=obj_data.get("profiles", []),
                )
            except Exception as e:
                # Log but continue loading other objects
                print(f"Warning: Failed to load object {obj_file}: {e}")

        return objects

    def _load_events(
        self, categories: dict[str, OcsfCategory]
    ) -> dict[str, OcsfEvent]:
        """Load all event class definitions from events/ directory.

        Args:
            categories: Already loaded categories for event classification

        Returns:
            Dictionary of event name -> OcsfEvent
        """
        events = {}
        events_dir = self.schema_path / "events"

        if not events_dir.exists():
            return events

        # Load base_event first
        base_event_path = events_dir / "base_event.json"
        if base_event_path.exists():
            events["base_event"] = self._load_event_file(
                base_event_path, "base_event", None
            )

        # Load events from each category directory
        for cat_name in categories:
            cat_dir = events_dir / cat_name
            if cat_dir.exists() and cat_dir.is_dir():
                self._load_events_from_category(cat_dir, cat_name, events)

        return events

    def _load_events_from_category(
        self, cat_dir: Path, category: str, events: dict[str, OcsfEvent]
    ) -> None:
        """Load events from a category directory.

        Args:
            cat_dir: Path to the category directory
            category: Category name
            events: Dictionary to populate with loaded events
        """
        for event_file in cat_dir.glob("*.json"):
            try:
                event_name = event_file.stem
                event = self._load_event_file(event_file, event_name, category)
                events[event_name] = event
            except Exception as e:
                print(f"Warning: Failed to load event {event_file}: {e}")

    def _load_event_file(
        self, path: Path, name: str, category: str | None
    ) -> OcsfEvent:
        """Load a single event file.

        Args:
            path: Path to the event JSON file
            name: Event name (filename without extension)
            category: Category name (from parent directory)

        Returns:
            Parsed OcsfEvent
        """
        event_data = self._load_json(path)
        attributes = self._parse_attributes(event_data.get("attributes", {}))

        return OcsfEvent(
            name=name,
            caption=event_data.get("caption", name),
            description=event_data.get("description", ""),
            uid=event_data.get("uid", 0),
            category=category or event_data.get("category", ""),
            extends=event_data.get("extends"),
            attributes=attributes,
            profiles=event_data.get("profiles", []),
            constraints=event_data.get("constraints"),
        )

    def _parse_attributes(self, attrs_data: dict) -> dict[str, OcsfAttribute]:
        """Parse attribute definitions from raw JSON.

        Args:
            attrs_data: Raw attributes dictionary from JSON

        Returns:
            Dictionary of attribute name -> OcsfAttribute
        """
        attributes = {}

        for attr_name, attr_data in attrs_data.items():
            # Skip $include directives (they're for profile inclusion)
            if attr_name.startswith("$"):
                continue

            # Handle attribute definition
            if isinstance(attr_data, dict):
                attr_type = attr_data.get("type")
                is_array = False

                # Check if type indicates an array
                if attr_type and attr_type.endswith("[]"):
                    is_array = True
                    attr_type = attr_type[:-2]  # Remove [] suffix

                # Check is_array flag
                if attr_data.get("is_array"):
                    is_array = True

                attributes[attr_name] = OcsfAttribute(
                    name=attr_name,
                    caption=attr_data.get("caption", attr_name),
                    description=attr_data.get("description", ""),
                    type=attr_type,
                    requirement=attr_data.get("requirement", "optional"),
                    is_array=is_array,
                    deprecated=attr_data.get("deprecated"),
                    enum=attr_data.get("enum"),
                    group=attr_data.get("group"),
                    observable=attr_data.get("observable"),
                    profile=attr_data.get("profile"),
                    sibling=attr_data.get("sibling"),
                    object_type=attr_data.get("object_type"),
                    object_name=attr_data.get("object_name"),
                )
            else:
                # Simple attribute reference (just a string or other value)
                attributes[attr_name] = OcsfAttribute(
                    name=attr_name,
                    caption=attr_name,
                    description="",
                )

        return attributes

    def get_version(self) -> str:
        """Get the OCSF schema version without loading the full schema.

        Returns:
            Version string (e.g., '1.8.0-dev')
        """
        version_data = self._load_json(self.schema_path / "version.json")
        return version_data.get("version", "unknown")

    def get_object(self, name: str) -> OcsfObject | None:
        """Load a single object definition.

        Args:
            name: Object name (e.g., 'device', 'process')

        Returns:
            OcsfObject or None if not found
        """
        obj_path = self.schema_path / "objects" / f"{name}.json"
        if not obj_path.exists():
            return None

        obj_data = self._load_json(obj_path)
        attributes = self._parse_attributes(obj_data.get("attributes", {}))

        return OcsfObject(
            name=name,
            caption=obj_data.get("caption", name),
            description=obj_data.get("description", ""),
            extends=obj_data.get("extends"),
            attributes=attributes,
            constraints=obj_data.get("constraints"),
            observable=obj_data.get("observable"),
            profiles=obj_data.get("profiles", []),
        )

    def list_objects(self) -> list[str]:
        """List all available object names.

        Returns:
            List of object names
        """
        objects_dir = self.schema_path / "objects"
        if not objects_dir.exists():
            return []
        return [f.stem for f in objects_dir.glob("*.json")]

    def list_events(self) -> list[str]:
        """List all available event names.

        Returns:
            List of event names
        """
        events_dir = self.schema_path / "events"
        if not events_dir.exists():
            return []

        event_names = []

        # Base event
        if (events_dir / "base_event.json").exists():
            event_names.append("base_event")

        # Events in category directories
        for subdir in events_dir.iterdir():
            if subdir.is_dir():
                for event_file in subdir.glob("*.json"):
                    event_names.append(event_file.stem)

        return event_names

    def get_dictionary_attribute(self, name: str) -> dict | None:
        """Get an attribute definition from the dictionary.

        Args:
            name: Attribute name

        Returns:
            Attribute definition dict or None
        """
        dictionary = self._load_json(self.schema_path / "dictionary.json")
        return dictionary.get("attributes", {}).get(name)

    def get_type_definition(self, type_name: str) -> dict | None:
        """Get a type definition from the dictionary.

        Args:
            type_name: Type name (e.g., 'string_t', 'ip_t')

        Returns:
            Type definition dict or None
        """
        dictionary = self._load_json(self.schema_path / "dictionary.json")
        types = dictionary.get("types", {}).get("attributes", {})
        return types.get(type_name)
