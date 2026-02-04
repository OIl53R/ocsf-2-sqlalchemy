# OCSF-to-SQLAlchemy Parser

## Project Overview
Parser that generates both Pydantic models (for validation/API) and SQLAlchemy models (for database ORM) from OCSF (Open Cybersecurity Schema Framework) schema.

## Key Design Decisions
- **Database**: PostgreSQL with full normalization (no JSONB, no flattening)
- **Array Handling**: Separate join/association tables
- **Inheritance**: SQLAlchemy Joined Table Inheritance for OCSF `extends`
- **Dual Models**: Pydantic for validation, SQLAlchemy for ORM

## Directory Structure
- `pydantic/` - Generated Pydantic models (via datamodel-code-generator)
- `sqlalchemy/` - Generated SQLAlchemy models (via Jinja2)
- `src/parser/` - Core parsing logic
- `src/jinja_templates/` - Jinja2 templates for code generation
- `tests/` - Unit, integration, and database tests

## Commands
```bash
# Run all tests
pytest

# Generate models
python main.py generate --ocsf-version 1.4.0-dev

# Lint and format
ruff check src/
black src/
```

## Type Mapping Reference
| OCSF Type | SQLAlchemy Type |
|-----------|-----------------|
| string_t | String(65535) or Text |
| integer_t | Integer |
| long_t | BigInteger |
| timestamp_t | BigInteger (ms since epoch) |
| ip_t | INET |
| uuid_t | Uuid |
| object_t | ForeignKey + relationship() |
