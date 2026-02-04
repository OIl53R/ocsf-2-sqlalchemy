# OCSF-to-SQLAlchemy Parser

Generate SQLAlchemy models from [OCSF (Open Cybersecurity Schema Framework)](https://github.com/ocsf/ocsf-schema) schema for PostgreSQL with full normalization.

## Features

- **Full Normalization**: No JSONB flattening - arrays become association tables
- **Type-Safe Models**: SQLAlchemy 2.0+ with `Mapped` type hints
- **PostgreSQL Native Types**: `INET` for IPs, `CIDR` for subnets, `UUID` for UUIDs
- **Inheritance Support**: Joined table inheritance for OCSF `extends` relationships
- **Metadata Tables**: Runtime-queryable schema documentation
- **Version Agnostic**: Works with any OCSF schema version

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ocsf-2-sqlalchemy.git
cd ocsf-2-sqlalchemy

# Initialize the OCSF schema submodule
git submodule update --init

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Show schema information
python main.py info

# Analyze the schema
python main.py analyze

# Generate models
python main.py generate --output ./generated_models
```

## Generated Structure

```
generated_models/
├── base.py                    # OcsfBase class
├── base_models/               # Object models (device, user, process, etc.)
│   ├── __init__.py
│   ├── device.py
│   ├── process.py
│   └── ...
├── events/                    # Event models (process_activity, etc.)
│   ├── __init__.py
│   ├── base_event.py
│   ├── process_activity.py
│   └── ...
├── relations/                 # Association tables for arrays
│   ├── __init__.py
│   └── ocsf_device_groups.py
└── metadata/                  # Schema metadata tables
    ├── __init__.py
    └── tables.py
```

## Configuration

### Custom Naming

```bash
python main.py generate \
    --table-prefix sec_ \
    --table-suffix _tbl \
    --class-prefix Sec \
    --class-suffix Model
```

### Environment Variables

Create a `.env` file:

```
DATABASE_URL=postgresql://user:password@localhost:5432/ocsf_db
OCSF_SCHEMA_PATH=./ocsf-schema
```

## Type Mapping

| OCSF Type | SQLAlchemy | PostgreSQL |
|-----------|------------|------------|
| `string_t` | `Text` | `TEXT` |
| `integer_t` | `Integer` | `INTEGER` |
| `long_t` | `BigInteger` | `BIGINT` |
| `timestamp_t` | `BigInteger` | `BIGINT` (ms epoch) |
| `ip_t` | `INET` | `INET` |
| `mac_t` | `String(17)` | `VARCHAR(17)` |
| `uuid_t` | `Uuid` | `UUID` |
| `subnet_t` | `CIDR` | `CIDR` |

## API Usage

```python
from src.parser import SchemaAnalyzer, CodeGenerator

# Analyze schema
analyzer = SchemaAnalyzer("./ocsf-schema")
analyzed = analyzer.analyze()

print(f"Version: {analyzed.version}")
print(f"Objects: {len(analyzed.objects)}")
print(f"Events: {len(analyzed.events)}")

# Generate models
generator = CodeGenerator(analyzer, "./output")
generator.write_all()
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Architecture

```
ocsf-schema (Git repo)
    → SchemaLoader (parse JSON files)
    → InheritanceResolver (resolve extends)
    → SchemaAnalyzer (analyze relationships)
    → CodeGenerator (Jinja2 templates)
    → SQLAlchemy Models
```

## Development

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Schema Coverage

- **171 Objects**: device, user, process, file, network_endpoint, etc.
- **84 Events**: process_activity, file_activity, network_activity, etc.
- **8 Categories**: System, Network, IAM, Findings, Application, Discovery, Remediation, Unmanned Systems

## License

MIT License - See LICENSE file for details.
