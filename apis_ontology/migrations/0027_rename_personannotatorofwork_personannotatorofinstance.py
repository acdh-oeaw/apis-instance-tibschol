# Generated by Django 4.2.15 on 2024-08-29 11:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("relations", "0001_initial"),
        ("apis_ontology", "0026_instance_dimension_versioninstance_dimension"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PersonAnnotatorOfWork",
            new_name="PersonAnnotatorOfInstance",
        ),
    ]
