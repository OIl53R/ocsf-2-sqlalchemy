"""Integration tests for the full OCSF to SQLAlchemy pipeline."""

import ast
import pytest
from pathlib import Path
from src.parser import SchemaAnalyzer, CodeGenerator, NamingConfig


class TestFullPipeline:
    """Test the complete schema-to-models pipeline."""

    @pytest.fixture
    def schema_path(self) -> Path:
        """Return the path to the OCSF schema."""
        return Path(__file__).parent.parent.parent / "ocsf-schema"

    @pytest.fixture
    def output_dir(self, tmp_path: Path) -> Path:
        """Return a temporary output directory."""
        return tmp_path / "generated"

    def test_full_generation_pipeline(
        self, schema_path: Path, output_dir: Path
    ) -> None:
        """Test complete generation from schema to files."""
        # Create analyzer
        analyzer = SchemaAnalyzer(schema_path)
        analyzed = analyzer.analyze()

        # Verify analysis
        assert analyzed.version is not None
        assert len(analyzed.objects) > 100
        assert len(analyzed.events) > 50
        assert len(analyzed.categories) >= 8

        # Create generator
        generator = CodeGenerator(analyzer, output_dir)

        # Generate files
        written = generator.write_all()

        # Verify files were created
        assert len(written) > 500  # Lots of files expected

        # Verify directory structure
        assert (output_dir / "base.py").exists()
        assert (output_dir / "base_models").is_dir()
        assert (output_dir / "events").is_dir()
        assert (output_dir / "relations").is_dir()
        assert (output_dir / "metadata").is_dir()

        # Verify key models exist
        assert (output_dir / "base_models" / "device.py").exists()
        assert (output_dir / "base_models" / "process.py").exists()
        assert (output_dir / "base_models" / "user.py").exists()
        assert (output_dir / "events" / "process_activity.py").exists()
        assert (output_dir / "events" / "base_event.py").exists()

        # Verify individual metadata files exist (not monolithic tables.py)
        assert (output_dir / "metadata" / "objects.py").exists()
        assert (output_dir / "metadata" / "attributes.py").exists()
        assert (output_dir / "metadata" / "enums.py").exists()
        assert (output_dir / "metadata" / "categories.py").exists()
        assert (output_dir / "metadata" / "event_classes.py").exists()
        assert not (output_dir / "metadata" / "tables.py").exists()

    def test_all_generated_files_are_valid_python(
        self, schema_path: Path, output_dir: Path
    ) -> None:
        """Test all generated files are syntactically valid Python."""
        analyzer = SchemaAnalyzer(schema_path)
        generator = CodeGenerator(analyzer, output_dir)
        written = generator.write_all()

        errors = []
        for path in written:
            if path.suffix == ".py":
                content = path.read_text()
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    errors.append(f"{path}: {e}")

        if errors:
            pytest.fail(f"Syntax errors in generated files:\n" + "\n".join(errors[:10]))

    def test_generation_with_custom_naming(
        self, schema_path: Path, output_dir: Path
    ) -> None:
        """Test generation with custom naming configuration."""
        analyzer = SchemaAnalyzer(schema_path)
        naming_config = NamingConfig(
            table_prefix="sec_",
            table_suffix="_tbl",
            class_prefix="Sec",
            class_suffix="Model",
        )
        generator = CodeGenerator(analyzer, output_dir, naming_config)
        written = generator.write_all()

        # Verify custom naming is applied
        device_path = output_dir / "base_models" / "device.py"
        content = device_path.read_text()

        assert "class SecDeviceModel" in content
        assert '__tablename__ = "sec_device_tbl"' in content

    def test_inheritance_chain_correct(
        self, schema_path: Path, output_dir: Path
    ) -> None:
        """Test that inheritance chains are generated correctly."""
        analyzer = SchemaAnalyzer(schema_path)
        analyzed = analyzer.analyze()

        # Check process_activity inheritance
        proc = analyzed.events.get("process_activity")
        assert proc is not None
        assert "process_activity" in proc.inheritance_chain
        assert "system" in proc.inheritance_chain

        # Check device inheritance
        device = analyzed.objects.get("device")
        assert device is not None
        assert "device" in device.inheritance_chain

    def test_relationships_detected(self, schema_path: Path) -> None:
        """Test that relationships are correctly detected."""
        analyzer = SchemaAnalyzer(schema_path)
        analyzed = analyzer.analyze()

        # Should find relationships
        assert len(analyzed.relationships) > 0

        # Find device -> location relationship
        device_rels = [
            r for r in analyzed.relationships
            if r.source_entity == "device"
        ]
        assert len(device_rels) > 0

    def test_array_attributes_detected(self, schema_path: Path) -> None:
        """Test that array attributes are correctly detected."""
        analyzer = SchemaAnalyzer(schema_path)
        analyzed = analyzer.analyze()

        # Should find array attributes
        assert len(analyzed.array_attributes) > 0

        # Find device.groups array
        groups = [
            a for a in analyzed.array_attributes
            if a.parent_entity == "device" and a.attribute_name == "groups"
        ]
        assert len(groups) > 0

    def test_enums_extracted(self, schema_path: Path) -> None:
        """Test that enums are correctly extracted."""
        analyzer = SchemaAnalyzer(schema_path)
        analyzed = analyzer.analyze()

        # Should find enums
        assert len(analyzed.enums) > 0

    def test_metadata_populator_data(self, schema_path: Path) -> None:
        """Test that metadata populator generates correct data."""
        from src.parser.metadata_populator import MetadataPopulator

        analyzer = SchemaAnalyzer(schema_path)
        populator = MetadataPopulator(analyzer)

        data = populator.get_population_data()

        assert len(data["objects"]) > 0
        assert len(data["attributes"]) > 0
        assert len(data["categories"]) >= 8

        # Verify structure
        obj = data["objects"][0]
        assert "name" in obj
        assert "caption" in obj
        assert "object_type" in obj
