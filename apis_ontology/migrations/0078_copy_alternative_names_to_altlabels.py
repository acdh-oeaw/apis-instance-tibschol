from django.db import migrations


def copy_alternative_names(apps, schema_editor):
    models_to_migrate = ["Person", "Place", "Work", "Instance"]
    for model_name in models_to_migrate:
        Model = apps.get_model("apis_ontology", model_name)
        for obj in Model.objects.exclude(alternative_names_legacy__isnull=True).exclude(alternative_names_legacy=""):
            raw = obj.alternative_names_legacy or ""
            items = [line.strip() for line in raw.splitlines() if line.strip()]
            obj.alternative_names = [{"label": item, "language": "bo"} for item in items]
            obj.save(update_fields=["alternative_names"])


class Migration(migrations.Migration):

    dependencies = [
        ("apis_ontology", "0077_rename_alternative_names_add_altlabels_field"),
    ]

    operations = [
        migrations.RunPython(copy_alternative_names, migrations.RunPython.noop),
    ]
