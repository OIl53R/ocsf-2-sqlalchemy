#!/usr/bin/env python3
"""OCSF to SQLAlchemy Parser - CLI Entry Point.

Generates Pydantic and SQLAlchemy models from OCSF schema.
"""

import argparse
import sys
from pathlib import Path

from src.parser import (
    SchemaAnalyzer,
    CodeGenerator,
    NamingConfig,
)
from src.parser.metadata_populator import MetadataPopulator


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate SQLAlchemy models from OCSF schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate models with default settings
  python main.py generate

  # Generate to custom directory
  python main.py generate --output ./models

  # Use custom naming prefix
  python main.py generate --table-prefix sec_ --class-prefix Sec

  # Just show schema info
  python main.py info
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate SQLAlchemy models from OCSF schema",
    )
    gen_parser.add_argument(
        "--schema-path",
        type=Path,
        default=Path("ocsf-schema"),
        help="Path to ocsf-schema repository (default: ./ocsf-schema)",
    )
    gen_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("generated_models"),
        help="Output directory for generated models (default: ./generated_models)",
    )
    gen_parser.add_argument(
        "--table-prefix",
        default="ocsf_",
        help="Prefix for table names (default: ocsf_)",
    )
    gen_parser.add_argument(
        "--table-suffix",
        default="",
        help="Suffix for table names (default: empty)",
    )
    gen_parser.add_argument(
        "--class-prefix",
        default="Ocsf",
        help="Prefix for Python class names (default: Ocsf)",
    )
    gen_parser.add_argument(
        "--class-suffix",
        default="",
        help="Suffix for Python class names (default: empty)",
    )
    gen_parser.add_argument(
        "--core-object",
        type=str,
        default=None,
        help="Generate models only for this object and its dependencies (e.g., 'vulnerability')",
    )
    gen_parser.add_argument(
        "--max-depth",
        type=int,
        default=3,
        help="Maximum relationship depth from core object (default: 3)",
    )
    gen_parser.add_argument(
        "--include-events",
        action="store_true",
        help="Include events referencing included objects (default: exclude)",
    )

    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Display OCSF schema information",
    )
    info_parser.add_argument(
        "--schema-path",
        type=Path,
        default=Path("ocsf-schema"),
        help="Path to ocsf-schema repository (default: ./ocsf-schema)",
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze OCSF schema and show statistics",
    )
    analyze_parser.add_argument(
        "--schema-path",
        type=Path,
        default=Path("ocsf-schema"),
        help="Path to ocsf-schema repository (default: ./ocsf-schema)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    try:
        if args.command == "generate":
            return cmd_generate(args)
        elif args.command == "info":
            return cmd_info(args)
        elif args.command == "analyze":
            return cmd_analyze(args)
        else:
            parser.print_help()
            return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise


def cmd_generate(args: argparse.Namespace) -> int:
    """Execute the generate command."""
    print(f"Loading OCSF schema from: {args.schema_path}")

    # Create analyzer
    analyzer = SchemaAnalyzer(args.schema_path)
    analyzed = analyzer.analyze()

    print(f"Schema version: {analyzed.version}")
    print(f"Found {len(analyzed.objects)} objects, {len(analyzed.events)} events")

    # Apply filtering if core-object specified
    if args.core_object:
        from src.parser.object_filter import ObjectFilter, FilterConfig

        config = FilterConfig(
            core_object=args.core_object,
            max_depth=args.max_depth,
            include_events=args.include_events,
        )

        obj_filter = ObjectFilter(analyzed)
        analyzed, filter_result = obj_filter.filter(config)

        print(f"\nFiltered to {len(filter_result.included_objects)} objects (depth {args.max_depth} from '{args.core_object}')")
        if filter_result.inheritance_additions:
            print(f"  + {len(filter_result.inheritance_additions)} inheritance parents added")
        if filter_result.included_events:
            print(f"  + {len(filter_result.included_events)} related events included")

    # Configure naming
    naming_config = NamingConfig(
        table_prefix=args.table_prefix,
        table_suffix=args.table_suffix,
        class_prefix=args.class_prefix,
        class_suffix=args.class_suffix,
    )

    # Create generator with optional filtered schema
    generator = CodeGenerator(
        analyzer,
        args.output,
        naming_config,
        analyzed_schema=analyzed if args.core_object else None,
    )

    print(f"Generating models to: {args.output}")
    written = generator.write_all()

    print(f"Generated {len(written)} files:")
    print(f"  - Base models: {sum(1 for p in written if 'base_models' in str(p))}")
    print(f"  - Event models: {sum(1 for p in written if '/events/' in str(p))}")
    print(f"  - Association tables: {sum(1 for p in written if 'relations' in str(p))}")
    print(f"  - Metadata: {sum(1 for p in written if 'metadata' in str(p))}")

    print("\nGeneration complete!")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    """Execute the info command."""
    from src.parser.schema_loader import SchemaLoader

    loader = SchemaLoader(args.schema_path)

    print("OCSF Schema Information")
    print("=" * 40)
    print(f"Version: {loader.get_version()}")
    print(f"Objects: {len(loader.list_objects())}")
    print(f"Events: {len(loader.list_events())}")

    print("\nObjects:")
    for name in sorted(loader.list_objects())[:10]:
        print(f"  - {name}")
    print("  ...")

    print("\nEvents:")
    for name in sorted(loader.list_events())[:10]:
        print(f"  - {name}")
    print("  ...")

    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute the analyze command."""
    print(f"Analyzing OCSF schema from: {args.schema_path}")

    analyzer = SchemaAnalyzer(args.schema_path)
    analyzed = analyzer.analyze()

    print("\nSchema Analysis")
    print("=" * 50)
    print(f"Version: {analyzed.version}")
    print()

    print("Objects by inheritance depth:")
    obj_depths = {}
    for name, obj in analyzed.objects.items():
        depth = len(obj.inheritance_chain) - 1
        obj_depths.setdefault(depth, []).append(name)
    for depth in sorted(obj_depths.keys()):
        print(f"  Depth {depth}: {len(obj_depths[depth])} objects")

    print()
    print("Events by category:")
    event_cats = {}
    for name, event in analyzed.events.items():
        cat = event.category or "uncategorized"
        event_cats.setdefault(cat, []).append(name)
    for cat in sorted(event_cats.keys()):
        print(f"  {cat}: {len(event_cats[cat])} events")

    print()
    print(f"Total relationships: {len(analyzed.relationships)}")
    print(f"  - Foreign keys: {sum(1 for r in analyzed.relationships if r.relationship_type == 'foreign_key')}")
    print(f"  - Association tables: {sum(1 for r in analyzed.relationships if r.relationship_type == 'association_table')}")

    print()
    print(f"Array attributes: {len(analyzed.array_attributes)}")
    print(f"  - Primitive arrays: {sum(1 for a in analyzed.array_attributes if a.is_primitive)}")
    print(f"  - Object arrays: {sum(1 for a in analyzed.array_attributes if not a.is_primitive)}")

    print()
    print(f"Enums: {len(analyzed.enums)}")
    total_values = sum(len(e.values) for e in analyzed.enums.values())
    print(f"  Total enum values: {total_values}")

    print()
    print(f"Categories: {len(analyzed.categories)}")
    for name, cat in sorted(analyzed.categories.items()):
        print(f"  - {name} (uid: {cat.uid})")

    return 0


if __name__ == "__main__":
    sys.exit(main())
