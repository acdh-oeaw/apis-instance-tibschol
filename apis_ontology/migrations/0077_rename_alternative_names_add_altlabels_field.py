# Rewritten to handle PostgreSQL type casting issue when converting TextField -> JSONField

import apis_ontology.fields
from django.db import migrations, models

MODELS = ["instance", "person", "place", "versioninstance", "versionperson", "versionplace", "versionwork", "work"]


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ("apis_ontology", "0076_alter_instance_tibetan_transliteration_and_more"),
    ]

    operations = (
        # Step 1: add legacy TextField columns
        [
            migrations.AddField(
                model_name=model,
                name="alternative_names_legacy",
                field=models.TextField(
                    blank=True, null=True, verbose_name="Alternative names (legacy)"
                ),
            )
            for model in MODELS
        ]
        # Step 2: copy existing text data into legacy columns, then NULL out the original
        + [
            migrations.RunSQL(
                sql=f"UPDATE apis_ontology_{model} SET alternative_names_legacy = alternative_names; "
                    f"UPDATE apis_ontology_{model} SET alternative_names = NULL;",
                reverse_sql=f"UPDATE apis_ontology_{model} SET alternative_names = alternative_names_legacy;",
            )
            for model in MODELS
        ]
        # Step 3: alter the now-empty alternative_names column to JSONField
        + [
            migrations.AlterField(
                model_name=model,
                name="alternative_names",
                field=apis_ontology.fields.AlternativeLabelsField(
                    blank=True, null=True, verbose_name="Alternative names"
                ),
            )
            for model in MODELS
        ]
    )
