# Generated by Django 4.2.13 on 2024-06-02 21:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0012_remove_instance_end_date_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="instance",
            name="published",
        ),
        migrations.RemoveField(
            model_name="person",
            name="published",
        ),
        migrations.RemoveField(
            model_name="place",
            name="published",
        ),
        migrations.RemoveField(
            model_name="versioninstance",
            name="published",
        ),
        migrations.RemoveField(
            model_name="versionperson",
            name="published",
        ),
        migrations.RemoveField(
            model_name="versionplace",
            name="published",
        ),
        migrations.RemoveField(
            model_name="versionwork",
            name="published",
        ),
        migrations.RemoveField(
            model_name="work",
            name="published",
        ),
    ]
