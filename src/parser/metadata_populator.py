"""OCSF Metadata Populator.

Populates the metadata tables with schema information at runtime.
"""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import insert
from sqlalchemy.orm import Session

from .schema_analyzer import SchemaAnalyzer, AnalyzedSchema


@dataclass
class MetadataPopulator:
    """Populates OCSF metadata tables from schema.

    The metadata tables store:
    - Object/event class definitions
    - Attribute definitions
    - Enum value mappings
    - Category information
    - Event class registry
    """

    analyzer: SchemaAnalyzer

    def populate_all(self, session: Session) -> dict[str, int]:
        """Populate all metadata tables.

        Args:
            session: SQLAlchemy session

        Returns:
            Dictionary of table name -> row count inserted
        """
        analyzed = self.analyzer.analyze()
        counts = {}

        counts["objects"] = self._populate_objects(session, analyzed)
        counts["attributes"] = self._populate_attributes(session, analyzed)
        counts["enums"] = self._populate_enums(session, analyzed)
        counts["categories"] = self._populate_categories(session, analyzed)
        counts["event_classes"] = self._populate_event_classes(session, analyzed)

        session.commit()
        return counts

    def _populate_objects(self, session: Session, analyzed: AnalyzedSchema) -> int:
        """Populate ocsf_metadata_objects table."""
        from sqlalchemy.sql import text

        count = 0

        # Insert objects
        for name, obj in analyzed.objects.items():
            session.execute(
                text("""
                    INSERT INTO ocsf_metadata_objects
                    (name, caption, description, object_type, extends, category, uid)
                    VALUES (:name, :caption, :description, :object_type, :extends, :category, :uid)
                    ON CONFLICT (name) DO UPDATE SET
                        caption = :caption,
                        description = :description,
                        extends = :extends
                """),
                {
                    "name": name,
                    "caption": obj.caption,
                    "description": obj.description,
                    "object_type": "object",
                    "extends": obj.extends,
                    "category": None,
                    "uid": None,
                },
            )
            count += 1

        # Insert events
        for name, event in analyzed.events.items():
            session.execute(
                text("""
                    INSERT INTO ocsf_metadata_objects
                    (name, caption, description, object_type, extends, category, uid)
                    VALUES (:name, :caption, :description, :object_type, :extends, :category, :uid)
                    ON CONFLICT (name) DO UPDATE SET
                        caption = :caption,
                        description = :description,
                        extends = :extends,
                        category = :category,
                        uid = :uid
                """),
                {
                    "name": name,
                    "caption": event.caption,
                    "description": event.description,
                    "object_type": "event",
                    "extends": event.extends,
                    "category": event.category,
                    "uid": event.uid,
                },
            )
            count += 1

        return count

    def _populate_attributes(
        self, session: Session, analyzed: AnalyzedSchema
    ) -> int:
        """Populate ocsf_metadata_attributes table."""
        from sqlalchemy.sql import text

        count = 0

        # Insert attributes from objects
        for obj_name, obj in analyzed.objects.items():
            for attr_name, attr in obj.all_attributes.items():
                session.execute(
                    text("""
                        INSERT INTO ocsf_metadata_attributes
                        (name, object_name, caption, description, ocsf_type,
                         requirement, is_array, is_inherited, source_object)
                        VALUES (:name, :object_name, :caption, :description, :ocsf_type,
                                :requirement, :is_array, :is_inherited, :source_object)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "name": attr_name,
                        "object_name": obj_name,
                        "caption": attr.caption,
                        "description": attr.description,
                        "ocsf_type": attr.ocsf_type,
                        "requirement": attr.requirement,
                        "is_array": attr.is_array,
                        "is_inherited": attr.is_inherited,
                        "source_object": attr.source_object,
                    },
                )
                count += 1

        # Insert attributes from events
        for event_name, event in analyzed.events.items():
            for attr_name, attr in event.all_attributes.items():
                session.execute(
                    text("""
                        INSERT INTO ocsf_metadata_attributes
                        (name, object_name, caption, description, ocsf_type,
                         requirement, is_array, is_inherited, source_object)
                        VALUES (:name, :object_name, :caption, :description, :ocsf_type,
                                :requirement, :is_array, :is_inherited, :source_object)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "name": attr_name,
                        "object_name": event_name,
                        "caption": attr.caption,
                        "description": attr.description,
                        "ocsf_type": attr.ocsf_type,
                        "requirement": attr.requirement,
                        "is_array": attr.is_array,
                        "is_inherited": attr.is_inherited,
                        "source_object": attr.source_object,
                    },
                )
                count += 1

        return count

    def _populate_enums(self, session: Session, analyzed: AnalyzedSchema) -> int:
        """Populate ocsf_metadata_enums table."""
        from sqlalchemy.sql import text

        count = 0

        for enum_name, enum_info in analyzed.enums.items():
            for value_id, caption in enum_info.values.items():
                session.execute(
                    text("""
                        INSERT INTO ocsf_metadata_enums
                        (enum_name, value_id, caption, description)
                        VALUES (:enum_name, :value_id, :caption, :description)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        "enum_name": enum_name,
                        "value_id": value_id,
                        "caption": caption,
                        "description": enum_info.description,
                    },
                )
                count += 1

        return count

    def _populate_categories(
        self, session: Session, analyzed: AnalyzedSchema
    ) -> int:
        """Populate ocsf_metadata_categories table."""
        from sqlalchemy.sql import text

        count = 0

        for name, category in analyzed.categories.items():
            session.execute(
                text("""
                    INSERT INTO ocsf_metadata_categories
                    (name, caption, description, uid)
                    VALUES (:name, :caption, :description, :uid)
                    ON CONFLICT (name) DO UPDATE SET
                        caption = :caption,
                        description = :description,
                        uid = :uid
                """),
                {
                    "name": name,
                    "caption": category.caption,
                    "description": category.description,
                    "uid": category.uid,
                },
            )
            count += 1

        return count

    def _populate_event_classes(
        self, session: Session, analyzed: AnalyzedSchema
    ) -> int:
        """Populate ocsf_metadata_event_classes table."""
        from sqlalchemy.sql import text

        count = 0

        for name, event in analyzed.events.items():
            if event.uid > 0:  # Only insert events with valid UIDs
                # Get category UID
                category_uid = 0
                if event.category and event.category in analyzed.categories:
                    category_uid = analyzed.categories[event.category].uid

                session.execute(
                    text("""
                        INSERT INTO ocsf_metadata_event_classes
                        (name, caption, description, uid, category_uid, extends)
                        VALUES (:name, :caption, :description, :uid, :category_uid, :extends)
                        ON CONFLICT (name) DO UPDATE SET
                            caption = :caption,
                            description = :description,
                            uid = :uid,
                            category_uid = :category_uid,
                            extends = :extends
                    """),
                    {
                        "name": name,
                        "caption": event.caption,
                        "description": event.description,
                        "uid": event.uid,
                        "category_uid": category_uid,
                        "extends": event.extends,
                    },
                )
                count += 1

        return count

    def get_population_data(self) -> dict[str, list[dict]]:
        """Get all metadata as dictionaries (for testing/inspection).

        Returns:
            Dictionary of table name -> list of row dicts
        """
        analyzed = self.analyzer.analyze()
        data = {
            "objects": [],
            "attributes": [],
            "enums": [],
            "categories": [],
            "event_classes": [],
        }

        # Collect objects
        for name, obj in analyzed.objects.items():
            data["objects"].append({
                "name": name,
                "caption": obj.caption,
                "description": obj.description,
                "object_type": "object",
                "extends": obj.extends,
            })

        for name, event in analyzed.events.items():
            data["objects"].append({
                "name": name,
                "caption": event.caption,
                "description": event.description,
                "object_type": "event",
                "extends": event.extends,
                "category": event.category,
                "uid": event.uid,
            })

        # Collect attributes
        for obj_name, obj in analyzed.objects.items():
            for attr_name, attr in obj.all_attributes.items():
                data["attributes"].append({
                    "name": attr_name,
                    "object_name": obj_name,
                    "caption": attr.caption,
                    "ocsf_type": attr.ocsf_type,
                    "requirement": attr.requirement,
                    "is_array": attr.is_array,
                    "is_inherited": attr.is_inherited,
                })

        # Collect enums
        for enum_name, enum_info in analyzed.enums.items():
            for value_id, caption in enum_info.values.items():
                data["enums"].append({
                    "enum_name": enum_name,
                    "value_id": value_id,
                    "caption": caption,
                })

        # Collect categories
        for name, cat in analyzed.categories.items():
            data["categories"].append({
                "name": name,
                "caption": cat.caption,
                "description": cat.description,
                "uid": cat.uid,
            })

        # Collect event classes
        for name, event in analyzed.events.items():
            if event.uid > 0:
                data["event_classes"].append({
                    "name": name,
                    "caption": event.caption,
                    "uid": event.uid,
                    "category": event.category,
                    "extends": event.extends,
                })

        return data
