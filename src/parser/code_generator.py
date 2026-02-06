"""OCSF to SQLAlchemy Code Generator.

Generates SQLAlchemy models from analyzed OCSF schema using Jinja2 templates.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schema_analyzer import (
    SchemaAnalyzer,
    AnalyzedSchema,
    ArrayAttributeInfo,
    RelationshipInfo,
)
from .inheritance_resolver import ResolvedObject, ResolvedEvent, ResolvedAttribute
from .type_mapper import TypeMapper
from .naming import NamingConvention, NamingConfig


@dataclass
class GeneratedFile:
    """Represents a generated Python file."""

    path: Path
    content: str
    entity_name: str | None = None
    file_type: str = "model"  # model, association, metadata, init


@dataclass
class ColumnInfo:
    """Column information for template rendering."""

    name: str
    sqlalchemy_type: str
    python_type: str
    nullable: bool
    is_foreign_key: bool = False
    references_table: str | None = None
    description: str = ""
    ocsf_type: str | None = None  # Original OCSF type for import collection


@dataclass
class RelationshipTemplateInfo:
    """Relationship information for template rendering."""

    name: str
    target_class: str
    target_entity: str  # Original entity name for import resolution
    is_array: bool
    association_table: str | None = None
    fk_column: str | None = None
    back_populates: str | None = None


@dataclass
class ImportInfo:
    """Import information for a generated file.

    Tracks all imports needed for a generated model file:
    - parent_import: Import statement for parent class (for inheritance)
    - relationship_imports: Import statements for relationship target classes
    - sqlalchemy_types: SQLAlchemy type names used in columns
    - needs_inet: Whether INET type from postgresql dialect is needed
    - needs_cidr: Whether CIDR type from postgresql dialect is needed
    - needs_relationship: Whether relationship() ORM import is needed
    - needs_timestamp_mixin: Whether OcsfTimestampMixin is needed
    - needs_list: Whether List typing import is needed
    """

    parent_import: str | None = None
    relationship_imports: list[str] = field(default_factory=list)
    sqlalchemy_types: set[str] = field(default_factory=set)
    needs_inet: bool = False
    needs_cidr: bool = False
    needs_relationship: bool = True
    needs_timestamp_mixin: bool = True
    needs_list: bool = True


class CodeGenerator:
    """Generates SQLAlchemy models from OCSF schema.

    Uses Jinja2 templates to generate:
    - Object models (base_models/)
    - Event models (events/)
    - Association tables (relations/)
    - Metadata tables (metadata/)
    """

    # Metadata table specifications for individual file generation
    METADATA_TABLE_SPECS = [
        {"template": "metadata/objects.py.j2", "filename": "objects.py",
         "class_name": "OcsfMetadataObjects", "sa_types": {"String", "Text", "Integer"}},
        {"template": "metadata/attributes.py.j2", "filename": "attributes.py",
         "class_name": "OcsfMetadataAttributes", "sa_types": {"String", "Text", "Boolean"}},
        {"template": "metadata/enums.py.j2", "filename": "enums.py",
         "class_name": "OcsfMetadataEnums", "sa_types": {"String", "Text", "Integer"}},
        {"template": "metadata/categories.py.j2", "filename": "categories.py",
         "class_name": "OcsfMetadataCategories", "sa_types": {"String", "Text", "Integer"}},
        {"template": "metadata/event_classes.py.j2", "filename": "event_classes.py",
         "class_name": "OcsfMetadataEventClasses", "sa_types": {"String", "Text", "Integer"}},
    ]

    # Map OCSF types to Python types for type hints
    PYTHON_TYPE_MAP = {
        "string_t": "str",
        "integer_t": "int",
        "long_t": "int",
        "float_t": "float",
        "boolean_t": "bool",
        "timestamp_t": "int",
        "datetime_t": "datetime",
        "json_t": "str",
        "ip_t": "str",
        "mac_t": "str",
        "uuid_t": "str",
        "subnet_t": "str",
        "port_t": "int",
        "hostname_t": "str",
        "email_t": "str",
        "url_t": "str",
        "path_t": "str",
        "file_hash_t": "str",
        "bytestring_t": "bytes",
    }

    # Python reserved keywords that need to be escaped in column names
    PYTHON_RESERVED = {
        "class", "type", "id", "from", "import", "return", "def", "if", "else",
        "elif", "for", "while", "try", "except", "finally", "with", "as",
        "pass", "break", "continue", "and", "or", "not", "in", "is", "lambda",
        "global", "nonlocal", "assert", "yield", "raise", "del", "True", "False",
        "None", "async", "await",
    }

    def _safe_column_name(self, name: str) -> str:
        """Escape Python reserved keywords in column names.

        Args:
            name: Original column name

        Returns:
            Safe column name (appends underscore if reserved)
        """
        if name in self.PYTHON_RESERVED:
            return f"{name}_"
        return name

    # Entity names that need underscore prefix in file names
    # These are internal/reserved names in OCSF
    UNDERSCORE_PREFIX_ENTITIES = {"entity", "dns"}

    def _get_module_path(self, entity_name: str, from_entity: str | None = None) -> str:
        """Get the module path for importing an entity.

        Converts entity names to module paths, handling special cases
        like _entity (underscore prefix for internal base types).

        Args:
            entity_name: The OCSF entity name (e.g., 'object', 'file', 'entity')
            from_entity: The entity doing the import (to avoid self-import)

        Returns:
            Module path for import (e.g., '.object', '._entity', '.file')
        """
        # Handle underscore-prefixed entities
        if entity_name in self.UNDERSCORE_PREFIX_ENTITIES:
            return f"._{entity_name}"
        return f".{entity_name}"

    def __init__(
        self,
        schema_analyzer: SchemaAnalyzer,
        output_dir: Path,
        naming_config: NamingConfig | None = None,
        analyzed_schema: AnalyzedSchema | None = None,
    ) -> None:
        """Initialize the code generator.

        Args:
            schema_analyzer: The schema analyzer with loaded schema
            output_dir: Directory to write generated files
            naming_config: Optional naming configuration
            analyzed_schema: Optional pre-analyzed schema (e.g., filtered).
                If provided, this is used instead of calling analyzer.analyze().
        """
        self.analyzer = schema_analyzer
        self.output_dir = Path(output_dir)
        self.naming = NamingConvention(naming_config)
        self.type_mapper = schema_analyzer.type_mapper
        self._analyzed_schema = analyzed_schema

        # Set up Jinja2 environment
        template_dir = Path(__file__).parent.parent / "jinja_templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def generate_all(self) -> list[GeneratedFile]:
        """Generate all SQLAlchemy models.

        Returns:
            List of GeneratedFile objects
        """
        # Use pre-analyzed schema if provided, otherwise analyze fresh
        analyzed = self._analyzed_schema if self._analyzed_schema else self.analyzer.analyze()
        files = []

        # Generate base module
        files.append(self._generate_base_module(analyzed))

        # Generate object models
        files.extend(self._generate_object_models(analyzed))

        # Generate event models
        files.extend(self._generate_event_models(analyzed))

        # Generate association tables
        files.extend(self._generate_association_tables(analyzed))

        # Generate metadata tables
        files.extend(self._generate_metadata_tables(analyzed))

        # Generate __init__.py files
        files.extend(self._generate_init_files(analyzed))

        return files

    def write_all(self) -> list[Path]:
        """Generate and write all files.

        Returns:
            List of paths to written files
        """
        files = self.generate_all()
        written = []

        for gen_file in files:
            full_path = self.output_dir / gen_file.path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(gen_file.content)
            written.append(full_path)

        return written

    def _generate_base_module(self, analyzed: AnalyzedSchema) -> GeneratedFile:
        """Generate the base module with OcsfBase class."""
        template = self.env.get_template("base/model_base.py.j2")
        content = template.render(
            schema_version=analyzed.version,
            description="Base classes for OCSF SQLAlchemy models.",
        )
        return GeneratedFile(
            path=Path("base.py"),
            content=content,
            file_type="base",
        )

    def _generate_object_models(
        self, analyzed: AnalyzedSchema
    ) -> list[GeneratedFile]:
        """Generate models for all objects."""
        files = []
        template = self.env.get_template("models/object_model.py.j2")

        # Generate in topological order
        for obj_name in analyzed.object_tree.topological_order:
            obj = analyzed.objects.get(obj_name)
            if not obj:
                continue

            context = self._build_object_context(obj, analyzed)
            content = template.render(**context)

            files.append(GeneratedFile(
                path=Path("base_models") / f"{obj_name}.py",
                content=self._add_file_header(
                    content, analyzed.version, "object", obj_name,
                    imports=context.get("imports"),
                ),
                entity_name=obj_name,
                file_type="object_model",
            ))

        return files

    def _generate_event_models(
        self, analyzed: AnalyzedSchema
    ) -> list[GeneratedFile]:
        """Generate models for all events."""
        files = []
        template = self.env.get_template("models/event_model.py.j2")

        # Generate in topological order
        for event_name in analyzed.event_tree.topological_order:
            event = analyzed.events.get(event_name)
            if not event:
                continue

            context = self._build_event_context(event, analyzed)
            content = template.render(**context)

            files.append(GeneratedFile(
                path=Path("events") / f"{event_name}.py",
                content=self._add_file_header(
                    content, analyzed.version, "event", event_name,
                    imports=context.get("imports"),
                ),
                entity_name=event_name,
                file_type="event_model",
            ))

        return files

    def _generate_association_tables(
        self, analyzed: AnalyzedSchema
    ) -> list[GeneratedFile]:
        """Generate association tables for array relationships."""
        files = []

        for arr_info in analyzed.array_attributes:
            if arr_info.is_primitive:
                # Primitive array -> separate table with value column
                content = self._generate_primitive_array_table(arr_info, analyzed)
            else:
                # Object array -> association table (many-to-many)
                content = self._generate_object_association_table(arr_info, analyzed)

            files.append(GeneratedFile(
                path=Path("relations") / f"{arr_info.association_table_name}.py",
                content=content,
                entity_name=arr_info.association_table_name,
                file_type="association",
            ))

        return files

    def _generate_primitive_array_table(
        self, arr_info: ArrayAttributeInfo, analyzed: AnalyzedSchema
    ) -> str:
        """Generate a table for primitive array values."""
        template = self.env.get_template("relations/primitive_array.py.j2")

        # Strip table prefix to avoid double Ocsf prefix in class name
        raw_name = arr_info.association_table_name.removeprefix(self.naming.config.table_prefix)
        class_name = self.naming.class_name(raw_name)
        parent_class = self.naming.class_name(arr_info.parent_entity)
        parent_table = self.naming.table_name(arr_info.parent_entity)

        # Get type mapping
        mapping = self.type_mapper.get_mapping(arr_info.element_type)
        sa_type_full = mapping.get_column_definition()  # e.g. "String(17)" or "Text"
        sa_type_base = mapping.sqlalchemy_type           # e.g. "String" or "Text"
        py_type = self.PYTHON_TYPE_MAP.get(arr_info.element_type, "str")

        content = template.render(
            class_name=class_name,
            table_name=arr_info.association_table_name,
            parent_entity=arr_info.parent_entity,
            attribute_name=arr_info.attribute_name,
            parent_class=parent_class,
            parent_table=parent_table,
            parent_fk_name=f"{self.naming.to_snake_case(arr_info.parent_entity)}_id",
            parent_relationship=self.naming.to_snake_case(arr_info.parent_entity),
            sqlalchemy_type=sa_type_full,
            python_type=py_type,
            nullable=True,
            description=f"Values for {arr_info.parent_entity}.{arr_info.attribute_name}",
        )

        # Build precise imports for primitive array tables
        imports = ImportInfo(
            sqlalchemy_types={"ForeignKey", "Integer"},
            needs_relationship=True,
            needs_timestamp_mixin=False,
            needs_list=False,
        )

        # Import the parent class for the relationship back-reference
        parent_module = self._get_module_path(arr_info.parent_entity).lstrip(".")
        if arr_info.parent_entity in analyzed.objects:
            parent_import = f"from ..base_models.{parent_module} import {parent_class}"
        else:
            parent_import = f"from ..events.{parent_module} import {parent_class}"
        imports.relationship_imports.append(parent_import)

        if sa_type_base == "INET":
            imports.needs_inet = True
        elif sa_type_base == "CIDR":
            imports.needs_cidr = True
        else:
            imports.sqlalchemy_types.add(sa_type_base)

        return self._add_file_header(
            content, analyzed.version, "primitive_array", arr_info.association_table_name,
            imports=imports,
        )

    def _generate_object_association_table(
        self, arr_info: ArrayAttributeInfo, analyzed: AnalyzedSchema
    ) -> str:
        """Generate an association table for object array relationships."""
        template = self.env.get_template("relations/association_table.py.j2")

        # Strip table prefix to avoid double Ocsf prefix in class name
        raw_name = arr_info.association_table_name.removeprefix(self.naming.config.table_prefix)
        class_name = self.naming.class_name(raw_name)

        parent_table = self.naming.table_name(arr_info.parent_entity)
        child_table = self.naming.table_name(arr_info.element_type)

        content = template.render(
            class_name=class_name,
            child_entity=arr_info.element_type,
            table_name=arr_info.association_table_name,
            parent_entity=arr_info.parent_entity,
            attribute_name=arr_info.attribute_name,
            parent_table=parent_table,
            child_table=child_table,
            parent_fk_name=f"{self.naming.to_snake_case(arr_info.parent_entity)}_id",
            child_fk_name=f"{self.naming.to_snake_case(arr_info.element_type)}_id",
            description=f"Association table for {arr_info.parent_entity}.{arr_info.attribute_name}",
        )

        # Build precise imports for association tables
        imports = ImportInfo(
            sqlalchemy_types={"ForeignKey", "Integer"},
            needs_relationship=False,
            needs_timestamp_mixin=False,
            needs_list=False,
        )

        return self._add_file_header(
            content, analyzed.version, "association", arr_info.association_table_name,
            imports=imports,
        )

    def _generate_metadata_tables(self, analyzed: AnalyzedSchema) -> list[GeneratedFile]:
        """Generate individual metadata table files."""
        files = []
        for spec in self.METADATA_TABLE_SPECS:
            template = self.env.get_template(spec["template"])
            content = template.render(
                schema_version=analyzed.version,
            )

            imports = ImportInfo(
                sqlalchemy_types=set(spec["sa_types"]),
                needs_relationship=False,
                needs_timestamp_mixin=True,
                needs_list=False,
            )

            files.append(GeneratedFile(
                path=Path("metadata") / spec["filename"],
                content=self._add_file_header(
                    content, analyzed.version, "metadata", spec["class_name"],
                    imports=imports,
                ),
                file_type="metadata",
            ))
        return files

    def _generate_init_files(self, analyzed: AnalyzedSchema) -> list[GeneratedFile]:
        """Generate __init__.py files for each package."""
        files = []

        # base_models/__init__.py
        object_class_names = [
            self.naming.class_name(name) for name in analyzed.object_tree.topological_order
        ]
        object_imports = [
            f"from .{name} import {self.naming.class_name(name)}"
            for name in analyzed.object_tree.topological_order
        ]
        files.append(GeneratedFile(
            path=Path("base_models") / "__init__.py",
            content=self._generate_init_content(
                object_imports, analyzed.version, class_names=object_class_names
            ),
            file_type="init",
        ))

        # events/__init__.py
        event_class_names = [
            self.naming.class_name(name) for name in analyzed.event_tree.topological_order
        ]
        event_imports = [
            f"from .{name} import {self.naming.class_name(name)}"
            for name in analyzed.event_tree.topological_order
        ]
        files.append(GeneratedFile(
            path=Path("events") / "__init__.py",
            content=self._generate_init_content(
                event_imports, analyzed.version, class_names=event_class_names
            ),
            file_type="init",
        ))

        # relations/__init__.py — explicit imports (no import *)
        relation_class_names = []
        relation_imports = []
        for arr in analyzed.array_attributes:
            raw_name = arr.association_table_name.removeprefix(self.naming.config.table_prefix)
            cls_name = self.naming.class_name(raw_name)
            relation_class_names.append(cls_name)
            relation_imports.append(
                f"from .{arr.association_table_name} import {cls_name}"
            )
        files.append(GeneratedFile(
            path=Path("relations") / "__init__.py",
            content=self._generate_init_content(
                relation_imports, analyzed.version, class_names=relation_class_names
            ),
            file_type="init",
        ))

        # metadata/__init__.py — individual file imports
        metadata_class_names = [
            "OcsfMetadataObjects",
            "OcsfMetadataAttributes",
            "OcsfMetadataEnums",
            "OcsfMetadataCategories",
            "OcsfMetadataEventClasses",
        ]
        metadata_imports = [
            "from .objects import OcsfMetadataObjects",
            "from .attributes import OcsfMetadataAttributes",
            "from .enums import OcsfMetadataEnums",
            "from .categories import OcsfMetadataCategories",
            "from .event_classes import OcsfMetadataEventClasses",
        ]
        files.append(GeneratedFile(
            path=Path("metadata") / "__init__.py",
            content=self._generate_init_content(
                metadata_imports, analyzed.version, class_names=metadata_class_names
            ),
            file_type="init",
        ))

        # Main __init__.py — comprehensive re-exports from all subpackages
        all_class_names = ["OcsfBase", "OcsfTimestampMixin"]
        all_class_names.extend(object_class_names)
        all_class_names.extend(event_class_names)
        all_class_names.extend(relation_class_names)
        all_class_names.extend(metadata_class_names)

        main_imports = [
            "from .base import OcsfBase, OcsfTimestampMixin",
            "from .base_models import *  # noqa: F403",
            "from .events import *  # noqa: F403",
            "from .relations import *  # noqa: F403",
            "from .metadata import *  # noqa: F403",
        ]
        files.append(GeneratedFile(
            path=Path("__init__.py"),
            content=self._generate_init_content(
                main_imports, analyzed.version, class_names=all_class_names
            ),
            file_type="init",
        ))

        return files

    def _build_object_context(
        self, obj: ResolvedObject, analyzed: AnalyzedSchema
    ) -> dict[str, Any]:
        """Build template context for an object model."""
        class_name = self.naming.class_name(obj.name)
        table_name = self.naming.table_name(obj.name)

        # Determine parent class
        parent_class = None
        parent_table = None
        if obj.extends:
            parent_class = self.naming.class_name(obj.extends)
            parent_table = self.naming.table_name(obj.extends)

        # Check if this is a polymorphic base (has children)
        is_polymorphic_base = obj.name in analyzed.object_tree.children

        # Build columns for own attributes only
        columns = self._build_columns(obj.own_attributes, analyzed)

        # Build relationships
        relationships = self._build_relationships(obj.name, obj.own_attributes, analyzed)

        context = {
            "class_name": class_name,
            "table_name": table_name,
            "caption": obj.caption,
            "description": obj.description,
            "extends": obj.extends,
            "parent_class": parent_class,
            "parent_table": parent_table,
            "is_polymorphic_base": is_polymorphic_base,
            "polymorphic_identity": self.naming.discriminator_value(obj.name),
            "inheritance_chain": obj.inheritance_chain,
            "columns": columns,
            "relationships": relationships,
        }

        # Collect imports after context is built
        context["imports"] = self._collect_imports(
            obj.name, context, file_type="object", analyzed=analyzed
        )

        return context

    def _build_event_context(
        self, event: ResolvedEvent, analyzed: AnalyzedSchema
    ) -> dict[str, Any]:
        """Build template context for an event model."""
        class_name = self.naming.class_name(event.name)
        table_name = self.naming.table_name(event.name)

        # Determine parent class
        parent_class = None
        parent_table = None
        if event.extends:
            parent_class = self.naming.class_name(event.extends)
            parent_table = self.naming.table_name(event.extends)

        # Check if this is a polymorphic base
        is_polymorphic_base = event.name in analyzed.event_tree.children

        # Build columns for own attributes only
        columns = self._build_columns(event.own_attributes, analyzed)

        # Build relationships
        relationships = self._build_relationships(event.name, event.own_attributes, analyzed)

        context = {
            "class_name": class_name,
            "table_name": table_name,
            "caption": event.caption,
            "description": event.description,
            "category": event.category,
            "uid": event.uid,
            "extends": event.extends,
            "parent_class": parent_class,
            "parent_table": parent_table,
            "is_polymorphic_base": is_polymorphic_base,
            "polymorphic_identity": self.naming.discriminator_value(event.name),
            "inheritance_chain": event.inheritance_chain,
            "columns": columns,
            "relationships": relationships,
        }

        # Collect imports after context is built
        context["imports"] = self._collect_imports(
            event.name, context, file_type="event", analyzed=analyzed
        )

        return context

    def _build_columns(
        self,
        attributes: dict[str, ResolvedAttribute],
        analyzed: AnalyzedSchema,
    ) -> list[ColumnInfo]:
        """Build column info list from attributes."""
        columns = []

        for attr_name, attr in attributes.items():
            # Skip array attributes (they become association tables)
            if attr.is_array:
                continue

            # Check if this is an object reference
            if attr.object_type or (
                attr.ocsf_type and self.type_mapper.is_object_type(attr.ocsf_type)
            ):
                # Foreign key column - Integer type for FK
                target = attr.object_type or attr.ocsf_type
                columns.append(ColumnInfo(
                    name=self.naming.foreign_key_column(attr_name),
                    sqlalchemy_type="Integer",
                    python_type="int",
                    nullable=attr.requirement != "required",
                    is_foreign_key=True,
                    references_table=self.naming.table_name(target),
                    description=attr.description,
                    ocsf_type="integer_t",  # FK columns are always Integer
                ))
            else:
                # Regular column
                ocsf_type = attr.ocsf_type or "string_t"
                sa_type = self.type_mapper.get_sqlalchemy_type(ocsf_type)
                py_type = self.PYTHON_TYPE_MAP.get(ocsf_type, "str")

                # Escape Python reserved keywords
                col_name = self._safe_column_name(self.naming.column_name(attr_name))

                columns.append(ColumnInfo(
                    name=col_name,
                    sqlalchemy_type=sa_type,
                    python_type=py_type,
                    nullable=attr.requirement != "required",
                    is_foreign_key=False,
                    description=attr.description,
                    ocsf_type=ocsf_type,
                ))

        return columns

    def _build_relationships(
        self,
        entity_name: str,
        attributes: dict[str, ResolvedAttribute],
        analyzed: AnalyzedSchema,
    ) -> list[RelationshipTemplateInfo]:
        """Build relationship info list from attributes."""
        relationships = []

        for attr_name, attr in attributes.items():
            # Check if this is an object reference
            target = attr.object_type
            if not target and attr.ocsf_type:
                if self.type_mapper.is_object_type(attr.ocsf_type):
                    target = attr.ocsf_type

            if not target:
                continue

            target_class = self.naming.class_name(target)

            if attr.is_array:
                # Many-to-many via association table
                assoc_table = self.naming.association_table_name(entity_name, attr_name)
                relationships.append(RelationshipTemplateInfo(
                    name=self.naming.relationship_name(attr_name),
                    target_class=target_class,
                    target_entity=target,
                    is_array=True,
                    association_table=assoc_table,
                    back_populates=self.naming.back_populates_name(entity_name),
                ))
            else:
                # One-to-many (foreign key)
                fk_col = self.naming.foreign_key_column(attr_name)
                relationships.append(RelationshipTemplateInfo(
                    name=self.naming.relationship_name(attr_name),
                    target_class=target_class,
                    target_entity=target,
                    is_array=False,
                    fk_column=fk_col,
                    back_populates=self.naming.back_populates_name(entity_name),
                ))

        return relationships

    def _collect_imports(
        self,
        entity_name: str,
        context: dict[str, Any],
        file_type: str = "object",
        analyzed: AnalyzedSchema | None = None,
    ) -> ImportInfo:
        """Collect all required imports for a generated model file.

        Analyzes the context to determine:
        1. Parent class import (for inheritance)
        2. Relationship target imports (for foreign keys and relationships)
        3. SQLAlchemy types based on actual column types

        Args:
            entity_name: The entity being generated
            context: The template context with columns, relationships, extends, etc.
            file_type: Type of file being generated ('object' or 'event')
            analyzed: The analyzed schema (for determining if targets are objects/events)

        Returns:
            ImportInfo with all required imports
        """
        imports = ImportInfo()

        # Helper to determine if an entity is an object (vs event)
        def is_object_entity(target: str) -> bool:
            if analyzed is None:
                return True  # Default to object if we don't have schema info
            return target in analyzed.objects

        # Helper to get the full import path for an entity
        def get_import_path(target: str, source_file_type: str) -> str:
            target_is_object = is_object_entity(target)
            module_name = self._get_module_path(target).lstrip(".")

            if source_file_type == "event":
                if target_is_object:
                    # Event importing from object: need to go up and into base_models
                    return f"from ..base_models.{module_name}"
                else:
                    # Event importing from event: same directory
                    return f"from .{module_name}"
            else:  # source is object
                if target_is_object:
                    # Object importing from object: same directory
                    return f"from .{module_name}"
                else:
                    # Object importing from event: need to go up and into events
                    return f"from ..events.{module_name}"

        # 1. Parent class import
        extends = context.get("extends")
        if extends:
            parent_class = self.naming.class_name(extends)
            import_path = get_import_path(extends, file_type)
            imports.parent_import = f"{import_path} import {parent_class}"

        # 2. Relationship target imports
        relationships = context.get("relationships", [])
        seen_targets = set()
        for rel in relationships:
            target_entity = rel.target_entity
            target_class = rel.target_class
            # Skip self-references and duplicates
            if target_entity == entity_name or target_entity in seen_targets:
                continue
            seen_targets.add(target_entity)
            import_path = get_import_path(target_entity, file_type)
            imports.relationship_imports.append(
                f"{import_path} import {target_class}"
            )

        # 3. SQLAlchemy types from columns
        columns = context.get("columns", [])
        for col in columns:
            ocsf_type = col.ocsf_type
            if not ocsf_type:
                continue

            # Get the mapping to determine what SQLAlchemy type is needed
            mapping = self.type_mapper.get_mapping(ocsf_type)
            sa_type = mapping.sqlalchemy_type

            # Check for PostgreSQL dialect types
            if sa_type == "INET":
                imports.needs_inet = True
            elif sa_type == "CIDR":
                imports.needs_cidr = True
            else:
                # Extract base type name (handle types like "String(17)")
                base_type = sa_type.split("(")[0]
                imports.sqlalchemy_types.add(base_type)

        # Always need ForeignKey if there are FK columns
        if any(col.is_foreign_key for col in columns):
            imports.sqlalchemy_types.add("ForeignKey")

        # Template-level imports: ForeignKey for joined table inheritance
        if context.get("extends"):
            imports.sqlalchemy_types.add("ForeignKey")

        # Template-level imports: String for polymorphic base discriminator column
        if context.get("is_polymorphic_base") and not context.get("extends"):
            imports.sqlalchemy_types.add("String")

        return imports

    def _add_file_header(
        self, content: str, version: str, file_type: str, entity_name: str,
        imports: ImportInfo | None = None,
    ) -> str:
        """Add a file header to generated content.

        When ImportInfo is provided, generates dynamic imports based on actual usage.
        Otherwise falls back to static imports for backwards compatibility.

        Args:
            content: The generated model content
            version: OCSF schema version
            file_type: Type of model (object, event, association, etc.)
            entity_name: Name of the entity
            imports: Optional ImportInfo with collected imports

        Returns:
            Content with file header prepended
        """
        # Start with docstring
        header_lines = [
            f'"""Generated {file_type} model: {entity_name}.',
            "",
            f"Auto-generated from OCSF schema version {version}.",
            "DO NOT EDIT MANUALLY.",
            '"""',
            "",
        ]

        if imports is not None:
            # Dynamic imports based on actual usage
            # Base imports
            if imports.needs_timestamp_mixin:
                header_lines.append("from ..base import OcsfBase, OcsfTimestampMixin")
            else:
                header_lines.append("from ..base import OcsfBase")

            # Parent class import (for inheritance)
            if imports.parent_import:
                header_lines.append(imports.parent_import)

            # Relationship target imports
            for rel_import in sorted(imports.relationship_imports):
                header_lines.append(rel_import)

            # Typing imports
            if imports.needs_list:
                header_lines.append("from typing import Optional, List")
            else:
                header_lines.append("from typing import Optional")

            # SQLAlchemy core imports (only what's needed)
            if imports.sqlalchemy_types:
                sorted_types = sorted(imports.sqlalchemy_types)
                header_lines.append(f"from sqlalchemy import {', '.join(sorted_types)}")

            # PostgreSQL dialect imports (only if needed)
            dialect_types = []
            if imports.needs_inet:
                dialect_types.append("INET")
            if imports.needs_cidr:
                dialect_types.append("CIDR")
            if dialect_types:
                header_lines.append(
                    f"from sqlalchemy.dialects.postgresql import {', '.join(dialect_types)}"
                )

            # ORM imports
            orm_parts = ["Mapped", "mapped_column"]
            if imports.needs_relationship:
                orm_parts.append("relationship")
            header_lines.append(f"from sqlalchemy.orm import {', '.join(orm_parts)}")
        else:
            # Fallback to static imports for backwards compatibility
            header_lines.extend([
                "from ..base import OcsfBase, OcsfTimestampMixin",
                "from datetime import datetime",
                "from typing import Optional, List",
                "from sqlalchemy import (",
                "    ForeignKey, String, Text, Integer, BigInteger, Float,",
                "    Boolean, DateTime, LargeBinary, Uuid, Table, Column, func,",
                ")",
                "from sqlalchemy.dialects.postgresql import INET, CIDR",
                "from sqlalchemy.orm import Mapped, mapped_column, relationship",
            ])

        header_lines.append("")  # Empty line before content
        header_lines.append("")  # Second empty line
        return "\n".join(header_lines) + content

    def _generate_init_content(
        self, imports: list[str], version: str, class_names: list[str] | None = None
    ) -> str:
        """Generate __init__.py content.

        Args:
            imports: List of import statements
            version: OCSF schema version
            class_names: Optional list of class names for __all__ export
        """
        header = f'''"""Generated OCSF models.

Auto-generated from OCSF schema version {version}.
"""

'''
        parts = [header]

        if class_names:
            all_items = ",\n".join(f'    "{name}"' for name in class_names)
            parts.append(f"__all__ = [\n{all_items},\n]\n\n")

        parts.append("\n".join(imports) + "\n")
        return "".join(parts)
