# Generated by Django 4.2.11 on 2024-04-22 06:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apis_ontology", "0002_person_versionperson_versionperson_collection"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="person",
            options={"verbose_name": "person", "verbose_name_plural": "Persons"},
        ),
    ]
