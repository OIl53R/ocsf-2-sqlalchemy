"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def ocsf_schema_path(project_root: Path) -> Path:
    """Return the OCSF schema directory path."""
    return project_root / "ocsf-schema"


@pytest.fixture
def sample_ocsf_types() -> dict:
    """Sample OCSF type definitions for testing."""
    return {
        "string_t": {"type": "string"},
        "integer_t": {"type": "integer"},
        "long_t": {"type": "long"},
        "float_t": {"type": "float"},
        "boolean_t": {"type": "boolean"},
        "timestamp_t": {"type": "timestamp"},
        "datetime_t": {"type": "datetime"},
        "json_t": {"type": "json"},
        "ip_t": {"type": "ip"},
        "mac_t": {"type": "mac"},
        "uuid_t": {"type": "uuid"},
        "subnet_t": {"type": "subnet"},
    }
