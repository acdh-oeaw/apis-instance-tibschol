from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Reset ID sequences to max values for all models"

    def handle(self, *args, **options):
        cursor = connection.cursor()
        # Replace "app_model" with your actual app name and model name
        # # BEGIN;
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_work_collection"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "apis_ontology_work_collection";
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_versionwork"','history_id'), coalesce(max("history_id"), 1), max("history_id") IS NOT null) FROM "apis_ontology_versionwork";
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_versionwork_collection"','m2m_history_id'), coalesce(max("m2m_history_id"), 1), max("m2m_history_id") IS NOT null) FROM "apis_ontology_versionwork_collection";
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_instance_collection"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "apis_ontology_instance_collection";
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_versioninstance"','history_id'), coalesce(max("history_id"), 1), max("history_id") IS NOT null) FROM "apis_ontology_versioninstance";
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_versioninstance_collection"','m2m_history_id'), coalesce(max("m2m_history_id"), 1), max("m2m_history_id") IS NOT null) FROM "apis_ontology_versioninstance_collection";
        # SELECT setval(pg_get_serial_sequence('"apis_ontology_zoteroentry"','id'), coalesce(max("id"), 1), max("id") IS NOT null) FROM "apis_ontology_zoteroentry";
        # COMMIT;

        cursor.execute(
            """SELECT setval(pg_get_serial_sequence('"apis_metainfo_rootobject"','id'),
            coalesce(max("id"), 1), max("id") IS NOT null)
            FROM "apis_metainfo_rootobject";
            """
        )
        cursor.execute(
            """SELECT setval(pg_get_serial_sequence('"relations_relation"','id'),
            coalesce(max("id"), 1), max("id") IS NOT null)
            FROM "relations_relation";
            """
        )
        self.stdout.write(self.style.SUCCESS("ID sequences have been reset."))
