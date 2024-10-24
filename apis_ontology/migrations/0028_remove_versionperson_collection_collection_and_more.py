# Generated by Django 4.2.16 on 2024-10-11 11:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "apis_ontology",
            "0027_rename_personannotatorofwork_personannotatorofinstance",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="versionperson_collection",
            name="collection",
        ),
        migrations.RemoveField(
            model_name="versionperson_collection",
            name="history",
        ),
        migrations.RemoveField(
            model_name="versionperson_collection",
            name="person",
        ),
        migrations.RemoveField(
            model_name="versionplace_collection",
            name="collection",
        ),
        migrations.RemoveField(
            model_name="versionplace_collection",
            name="history",
        ),
        migrations.RemoveField(
            model_name="versionplace_collection",
            name="place",
        ),
        migrations.RemoveField(
            model_name="versionwork_collection",
            name="collection",
        ),
        migrations.RemoveField(
            model_name="versionwork_collection",
            name="history",
        ),
        migrations.RemoveField(
            model_name="versionwork_collection",
            name="work",
        ),
        migrations.AlterModelOptions(
            name="versioninstance",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical instance",
                "verbose_name_plural": "historical Instances",
            },
        ),
        migrations.AlterModelOptions(
            name="versionperson",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical person",
                "verbose_name_plural": "historical Persons",
            },
        ),
        migrations.AlterModelOptions(
            name="versionplace",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical place",
                "verbose_name_plural": "historical Places",
            },
        ),
        migrations.AlterModelOptions(
            name="versionwork",
            options={
                "get_latest_by": ("history_date", "history_id"),
                "ordering": ("-history_date", "-history_id"),
                "verbose_name": "historical work",
                "verbose_name_plural": "historical Works",
            },
        ),
        migrations.RemoveField(
            model_name="instance",
            name="collection",
        ),
        migrations.RemoveField(
            model_name="person",
            name="collection",
        ),
        migrations.RemoveField(
            model_name="place",
            name="collection",
        ),
        migrations.RemoveField(
            model_name="work",
            name="collection",
        ),
        migrations.DeleteModel(
            name="VersionInstance_collection",
        ),
        migrations.DeleteModel(
            name="VersionPerson_collection",
        ),
        migrations.DeleteModel(
            name="VersionPlace_collection",
        ),
        migrations.DeleteModel(
            name="VersionWork_collection",
        ),
    ]
