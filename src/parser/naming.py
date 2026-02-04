"""Naming convention utilities for OCSF to SQLAlchemy conversion.

Provides consistent naming transformations for tables, columns, and Python classes.
"""

import re
from dataclasses import dataclass, field


@dataclass
class NamingConfig:
    """Configuration for naming conventions."""

    table_prefix: str = "ocsf_"
    table_suffix: str = ""
    class_prefix: str = "Ocsf"
    class_suffix: str = ""


class NamingConvention:
    """Handles naming conventions for generated code.

    Provides utilities for converting between naming styles:
    - snake_case (for table names, column names)
    - PascalCase (for Python class names)

    Also handles prefixes/suffixes for tables and classes.
    """

    def __init__(self, config: NamingConfig | None = None) -> None:
        """Initialize with optional configuration.

        Args:
            config: Naming configuration, uses defaults if not provided
        """
        self.config = config or NamingConfig()

    def to_snake_case(self, name: str) -> str:
        """Convert a string to snake_case.

        Handles:
        - PascalCase: ProcessActivity -> process_activity
        - camelCase: processActivity -> process_activity
        - kebab-case: process-activity -> process_activity
        - Consecutive capitals: HTTPServer -> http_server
        - Numbers: Process2Activity -> process2_activity

        Args:
            name: The string to convert

        Returns:
            snake_case version of the string
        """
        if not name:
            return name

        # Replace hyphens and spaces with underscores
        name = name.replace("-", "_").replace(" ", "_")

        # Handle consecutive uppercase letters (e.g., HTTP -> http)
        # Insert underscore before a capital followed by lowercase
        name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)

        # Insert underscore before capital letters preceded by lowercase
        name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)

        # Convert to lowercase
        result = name.lower()

        # Clean up multiple underscores
        result = re.sub(r"_+", "_", result)

        # Remove leading/trailing underscores
        return result.strip("_")

    def to_pascal_case(self, name: str) -> str:
        """Convert a string to PascalCase.

        Handles:
        - snake_case: process_activity -> ProcessActivity
        - kebab-case: process-activity -> ProcessActivity
        - Already PascalCase: ProcessActivity -> ProcessActivity

        Args:
            name: The string to convert

        Returns:
            PascalCase version of the string
        """
        if not name:
            return name

        # Split by underscores, hyphens, and spaces
        parts = re.split(r"[_\-\s]+", name)

        # Capitalize each part
        return "".join(word.capitalize() for word in parts if word)

    def to_camel_case(self, name: str) -> str:
        """Convert a string to camelCase.

        Args:
            name: The string to convert

        Returns:
            camelCase version of the string
        """
        pascal = self.to_pascal_case(name)
        if not pascal:
            return pascal
        return pascal[0].lower() + pascal[1:]

    def table_name(self, name: str) -> str:
        """Generate a table name from an OCSF object/event name.

        Applies snake_case conversion and configured prefix/suffix.

        Args:
            name: The OCSF object or event class name

        Returns:
            PostgreSQL table name (e.g., 'ocsf_process_activity')
        """
        snake = self.to_snake_case(name)
        return f"{self.config.table_prefix}{snake}{self.config.table_suffix}"

    def class_name(self, name: str) -> str:
        """Generate a Python class name from an OCSF object/event name.

        Applies PascalCase conversion and configured prefix/suffix.

        Args:
            name: The OCSF object or event class name

        Returns:
            Python class name (e.g., 'OcsfProcessActivity')
        """
        pascal = self.to_pascal_case(name)
        return f"{self.config.class_prefix}{pascal}{self.config.class_suffix}"

    def column_name(self, name: str) -> str:
        """Generate a column name from an OCSF attribute name.

        Args:
            name: The OCSF attribute name

        Returns:
            PostgreSQL column name in snake_case
        """
        return self.to_snake_case(name)

    def foreign_key_column(self, relationship_name: str) -> str:
        """Generate a foreign key column name.

        Args:
            relationship_name: The name of the relationship

        Returns:
            FK column name (e.g., 'device_id')
        """
        snake = self.to_snake_case(relationship_name)
        return f"{snake}_id"

    def association_table_name(self, parent_name: str, attribute_name: str) -> str:
        """Generate an association table name for array relationships.

        Args:
            parent_name: The parent table/object name
            attribute_name: The array attribute name

        Returns:
            Association table name (e.g., 'ocsf_process_loaded_modules')
        """
        parent_snake = self.to_snake_case(parent_name)
        attr_snake = self.to_snake_case(attribute_name)
        return f"{self.config.table_prefix}{parent_snake}_{attr_snake}"

    def relationship_name(self, name: str) -> str:
        """Generate a SQLAlchemy relationship attribute name.

        Args:
            name: The OCSF attribute name

        Returns:
            Python attribute name in snake_case
        """
        return self.to_snake_case(name)

    def back_populates_name(self, parent_name: str) -> str:
        """Generate the back_populates name for a relationship.

        Args:
            parent_name: The parent table/object name

        Returns:
            back_populates attribute name (e.g., 'process_activities')
        """
        snake = self.to_snake_case(parent_name)
        # Simple pluralization (handles most cases)
        if snake.endswith("y"):
            return f"{snake[:-1]}ies"
        elif snake.endswith("s") or snake.endswith("x") or snake.endswith("ch"):
            return f"{snake}es"
        else:
            return f"{snake}s"

    def enum_name(self, name: str) -> str:
        """Generate an enum class name.

        Args:
            name: The OCSF enum name

        Returns:
            Python enum class name (e.g., 'OcsfActivityId')
        """
        pascal = self.to_pascal_case(name)
        return f"{self.config.class_prefix}{pascal}"

    def enum_value_name(self, name: str) -> str:
        """Generate an enum value name.

        Args:
            name: The OCSF enum value name

        Returns:
            Python enum value name in UPPER_SNAKE_CASE
        """
        return self.to_snake_case(name).upper()

    def pydantic_class_name(self, name: str) -> str:
        """Generate a Pydantic schema class name.

        Args:
            name: The OCSF object or event class name

        Returns:
            Pydantic class name (e.g., 'ProcessActivitySchema')
        """
        pascal = self.to_pascal_case(name)
        return f"{pascal}Schema"

    def discriminator_value(self, name: str) -> str:
        """Generate a discriminator value for polymorphic identity.

        Args:
            name: The OCSF object or event class name

        Returns:
            Discriminator string value (e.g., 'process_activity')
        """
        return self.to_snake_case(name)
