"""Tests for the OCSF code generator."""

import pytest
from pathlib import Path
from src.parser.schema_analyzer import SchemaAnalyzer
from src.parser.code_generator import CodeGenerator, GeneratedFile, ColumnInfo, ImportInfo


class TestCodeGenerator:
    """Test suite for CodeGenerator class."""

    @pytest.fixture
    def schema_path(self) -> Path:
        """Return the path to the OCSF schema."""
        return Path(__file__).parent.parent.parent / "ocsf-schema"

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Return a temporary output directory."""
        return tmp_path / "generated"

    @pytest.fixture
    def analyzer(self, schema_path: Path) -> SchemaAnalyzer:
        """Create a SchemaAnalyzer instance."""
        return SchemaAnalyzer(schema_path)

    @pytest.fixture
    def generator(self, analyzer: SchemaAnalyzer, output_dir: Path) -> CodeGenerator:
        """Create a CodeGenerator instance."""
        return CodeGenerator(analyzer, output_dir)


class TestGeneratorInitialization(TestCodeGenerator):
    """Tests for generator initialization."""

    def test_generator_creation(
        self, analyzer: SchemaAnalyzer, output_dir: Path
    ) -> None:
        """Test generator can be created."""
        generator = CodeGenerator(analyzer, output_dir)
        assert generator is not None

    def test_generator_has_jinja_env(self, generator: CodeGenerator) -> None:
        """Test generator has Jinja2 environment."""
        assert generator.env is not None


class TestFileGeneration(TestCodeGenerator):
    """Tests for file generation."""

    def test_generate_all_returns_files(self, generator: CodeGenerator) -> None:
        """Test generate_all returns list of GeneratedFile."""
        files = generator.generate_all()
        assert isinstance(files, list)
        assert len(files) > 0
        assert all(isinstance(f, GeneratedFile) for f in files)

    def test_generated_files_have_content(self, generator: CodeGenerator) -> None:
        """Test generated files have content."""
        files = generator.generate_all()
        for f in files:
            assert f.content is not None
            assert len(f.content) > 0

    def test_generates_base_module(self, generator: CodeGenerator) -> None:
        """Test generates base.py module."""
        files = generator.generate_all()
        base_files = [f for f in files if f.path == Path("base.py")]
        assert len(base_files) == 1
        assert "OcsfBase" in base_files[0].content

    def test_generates_object_models(self, generator: CodeGenerator) -> None:
        """Test generates object models."""
        files = generator.generate_all()
        object_files = [f for f in files if str(f.path).startswith("base_models/")]
        assert len(object_files) > 0

    def test_generates_event_models(self, generator: CodeGenerator) -> None:
        """Test generates event models."""
        files = generator.generate_all()
        event_files = [f for f in files if str(f.path).startswith("events/")]
        assert len(event_files) > 0

    def test_generates_association_tables(self, generator: CodeGenerator) -> None:
        """Test generates association tables."""
        files = generator.generate_all()
        relation_files = [f for f in files if str(f.path).startswith("relations/")]
        # Should have some association tables
        assert len(relation_files) > 0

    def test_generates_metadata_tables(self, generator: CodeGenerator) -> None:
        """Test generates 5 individual metadata files."""
        files = generator.generate_all()
        metadata_files = [
            f for f in files
            if str(f.path).startswith("metadata/") and f.path.name != "__init__.py"
        ]
        assert len(metadata_files) == 5
        filenames = {f.path.name for f in metadata_files}
        assert filenames == {
            "objects.py", "attributes.py", "enums.py",
            "categories.py", "event_classes.py",
        }

    def test_no_monolithic_metadata_tables_file(self, generator: CodeGenerator) -> None:
        """Test that the old monolithic tables.py is NOT generated."""
        files = generator.generate_all()
        tables_files = [
            f for f in files if f.path == Path("metadata") / "tables.py"
        ]
        assert len(tables_files) == 0

    def test_metadata_files_have_ocsf_base_import(self, generator: CodeGenerator) -> None:
        """Test each metadata file imports OcsfBase and OcsfTimestampMixin."""
        files = generator.generate_all()
        metadata_files = [
            f for f in files
            if str(f.path).startswith("metadata/") and f.path.name != "__init__.py"
        ]
        for f in metadata_files:
            assert "from ..base import OcsfBase, OcsfTimestampMixin" in f.content, (
                f"{f.path} missing OcsfBase import"
            )

    def test_association_table_has_minimal_imports(self, generator: CodeGenerator) -> None:
        """Test association tables don't have bloated static imports."""
        files = generator.generate_all()
        assoc_files = [f for f in files if f.file_type == "association"]
        assert len(assoc_files) > 0
        for f in assoc_files:
            # Extract import lines only (before class definition)
            import_section = f.content.split("class")[0]
            import_lines = [
                line.strip() for line in import_section.splitlines()
                if line.strip().startswith(("from ", "import "))
            ]
            import_text = "\n".join(import_lines)
            assert "LargeBinary" not in import_text
            assert "Table," not in import_text
            assert "Column," not in import_text
            assert "func" not in import_text

    def test_main_init_exports_all_subpackages(self, generator: CodeGenerator) -> None:
        """Test main __init__.py re-exports from all subpackages."""
        files = generator.generate_all()
        main_init = [f for f in files if f.path == Path("__init__.py")]
        assert len(main_init) == 1
        content = main_init[0].content
        assert "from .base_models import *" in content
        assert "from .events import *" in content
        assert "from .relations import *" in content
        assert "from .metadata import *" in content
        assert "__all__" in content
        # Should have many entries in __all__
        assert content.count('"Ocsf') > 10

    def test_generates_init_files(self, generator: CodeGenerator) -> None:
        """Test generates __init__.py files."""
        files = generator.generate_all()
        init_files = [f for f in files if f.path.name == "__init__.py"]
        # Should have init files for main, base_models, events, relations, metadata
        assert len(init_files) >= 5


class TestModelContent(TestCodeGenerator):
    """Tests for model content correctness."""

    def test_object_model_has_class(self, generator: CodeGenerator) -> None:
        """Test object models have class definition."""
        files = generator.generate_all()
        device_files = [
            f for f in files
            if f.entity_name == "device" and f.file_type == "object_model"
        ]
        if len(device_files) > 0:
            content = device_files[0].content
            assert "class OcsfDevice" in content

    def test_event_model_has_class(self, generator: CodeGenerator) -> None:
        """Test event models have class definition."""
        files = generator.generate_all()
        proc_files = [
            f for f in files
            if f.entity_name == "process_activity" and f.file_type == "event_model"
        ]
        if len(proc_files) > 0:
            content = proc_files[0].content
            assert "class OcsfProcessActivity" in content

    def test_model_has_tablename(self, generator: CodeGenerator) -> None:
        """Test models have __tablename__."""
        files = generator.generate_all()
        for f in files:
            if f.file_type in ("object_model", "event_model"):
                assert "__tablename__" in f.content

    def test_model_has_id_column(self, generator: CodeGenerator) -> None:
        """Test models have id column."""
        files = generator.generate_all()
        for f in files:
            if f.file_type in ("object_model", "event_model"):
                assert "id: Mapped[int]" in f.content

    def test_model_has_mapped_columns(self, generator: CodeGenerator) -> None:
        """Test models use mapped_column."""
        files = generator.generate_all()
        for f in files:
            if f.file_type in ("object_model", "event_model"):
                assert "mapped_column" in f.content


class TestWriteOutput(TestCodeGenerator):
    """Tests for writing files to disk."""

    def test_write_all_creates_files(
        self, generator: CodeGenerator, output_dir: Path
    ) -> None:
        """Test write_all creates files on disk."""
        output_dir.mkdir(parents=True, exist_ok=True)
        written = generator.write_all()

        assert len(written) > 0
        for path in written:
            assert path.exists()

    def test_write_creates_directories(
        self, generator: CodeGenerator, output_dir: Path
    ) -> None:
        """Test write_all creates necessary directories."""
        written = generator.write_all()

        expected_dirs = ["base_models", "events", "relations", "metadata"]
        for dir_name in expected_dirs:
            assert (output_dir / dir_name).is_dir()

    def test_written_files_are_valid_python(
        self, generator: CodeGenerator, output_dir: Path
    ) -> None:
        """Test written files are syntactically valid Python."""
        written = generator.write_all()

        # Check a sample of files for syntax validity
        for path in written[:10]:
            if path.suffix == ".py":
                content = path.read_text()
                try:
                    compile(content, str(path), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {path}: {e}")


class TestColumnInfo(TestCodeGenerator):
    """Tests for ColumnInfo dataclass."""

    def test_column_info_creation(self) -> None:
        """Test ColumnInfo can be created."""
        col = ColumnInfo(
            name="test_col",
            sqlalchemy_type="String",
            python_type="str",
            nullable=True,
        )
        assert col.name == "test_col"
        assert col.nullable is True

    def test_column_info_foreign_key(self) -> None:
        """Test ColumnInfo with foreign key."""
        col = ColumnInfo(
            name="device_id",
            sqlalchemy_type="Integer",
            python_type="int",
            nullable=True,
            is_foreign_key=True,
            references_table="ocsf_device",
        )
        assert col.is_foreign_key is True
        assert col.references_table == "ocsf_device"


class TestInheritanceGeneration(TestCodeGenerator):
    """Tests for inheritance handling in generation."""

    def test_child_model_has_fk_to_parent(self, generator: CodeGenerator) -> None:
        """Test child models have FK to parent table."""
        files = generator.generate_all()

        # Find a child event (like process_activity)
        proc_files = [
            f for f in files
            if f.entity_name == "process_activity" and f.file_type == "event_model"
        ]
        if len(proc_files) > 0:
            content = proc_files[0].content
            # Should have FK to parent (system)
            assert "ForeignKey" in content

    def test_polymorphic_base_has_discriminator(
        self, generator: CodeGenerator
    ) -> None:
        """Test polymorphic base classes have discriminator column."""
        files = generator.generate_all()

        # base_event should be a polymorphic base
        base_files = [
            f for f in files
            if f.entity_name == "base_event" and f.file_type == "event_model"
        ]
        if len(base_files) > 0:
            content = base_files[0].content
            # Should have _type discriminator or mapper args
            assert "polymorphic" in content.lower() or "_type" in content


class TestDynamicImports(TestCodeGenerator):
    """Tests for dynamic import generation."""

    def test_child_object_imports_parent(self, generator: CodeGenerator) -> None:
        """Test child object models import their parent class."""
        files = generator.generate_all()

        # Find _entity.py which extends object
        entity_files = [
            f for f in files
            if f.entity_name == "_entity" and f.file_type == "object_model"
        ]
        if len(entity_files) > 0:
            content = entity_files[0].content
            # Should import OcsfObject from object.py
            assert "from .object import OcsfObject" in content

    def test_object_imports_relationship_targets(self, generator: CodeGenerator) -> None:
        """Test object models import relationship target classes."""
        files = generator.generate_all()

        # Find affected_code which has relationships to file, user, etc.
        affected_files = [
            f for f in files
            if f.entity_name == "affected_code" and f.file_type == "object_model"
        ]
        if len(affected_files) > 0:
            content = affected_files[0].content
            # Should import related classes
            assert "from .file import OcsfFile" in content
            assert "from .user import OcsfUser" in content

    def test_event_imports_object_from_base_models(self, generator: CodeGenerator) -> None:
        """Test event models import objects from base_models directory."""
        files = generator.generate_all()

        # Find base_event which has relationships to metadata, observable, etc.
        base_event_files = [
            f for f in files
            if f.entity_name == "base_event" and f.file_type == "event_model"
        ]
        if len(base_event_files) > 0:
            content = base_event_files[0].content
            # Should import from ../base_models/
            assert "from ..base_models." in content
            # Shouldn't import objects from same directory (wrong path)
            assert "from .metadata import" not in content

    def test_child_event_imports_parent_event(self, generator: CodeGenerator) -> None:
        """Test child events import parent events from same directory."""
        files = generator.generate_all()

        # Find process_activity which extends system
        proc_files = [
            f for f in files
            if f.entity_name == "process_activity" and f.file_type == "event_model"
        ]
        if len(proc_files) > 0:
            content = proc_files[0].content
            # Should import parent event from same directory
            assert "from .system import OcsfSystem" in content

    def test_no_unused_sqlalchemy_imports(self, generator: CodeGenerator) -> None:
        """Test that files don't have excessive unused SQLAlchemy imports."""
        files = generator.generate_all()

        # Find a simple child model with no columns of its own
        network_proxy_files = [
            f for f in files
            if f.entity_name == "network_proxy" and f.file_type == "object_model"
        ]
        if len(network_proxy_files) > 0:
            content = network_proxy_files[0].content
            # Should not import types it doesn't use
            assert "LargeBinary" not in content
            assert "INET" not in content or "INET" in content.split("class")[1]  # Only in class, not imports

    def test_inet_imported_when_used(self, generator: CodeGenerator) -> None:
        """Test INET is imported only when ip_t type is used."""
        files = generator.generate_all()

        # Find endpoint.py which has IP address fields
        endpoint_files = [
            f for f in files
            if f.entity_name == "endpoint" and f.file_type == "object_model"
        ]
        if len(endpoint_files) > 0:
            content = endpoint_files[0].content
            # Should import INET from postgresql dialect
            assert "from sqlalchemy.dialects.postgresql import INET" in content

    def test_polymorphic_base_imports_string(self, generator: CodeGenerator) -> None:
        """Test polymorphic base classes import String for discriminator column."""
        files = generator.generate_all()

        # Find object.py which is a polymorphic base
        object_files = [
            f for f in files
            if f.entity_name == "object" and f.file_type == "object_model"
        ]
        if len(object_files) > 0:
            content = object_files[0].content
            # Should import String for discriminator column
            assert "from sqlalchemy import String" in content
            # But not other types it doesn't use
            assert "LargeBinary" not in content

    def test_underscore_prefix_entity_import(self, generator: CodeGenerator) -> None:
        """Test entities with underscore prefix are imported correctly."""
        files = generator.generate_all()

        # Find endpoint.py which extends _entity
        endpoint_files = [
            f for f in files
            if f.entity_name == "endpoint" and f.file_type == "object_model"
        ]
        if len(endpoint_files) > 0:
            content = endpoint_files[0].content
            # Should import from ._entity (underscore prefix)
            assert "from ._entity import OcsfEntity" in content
