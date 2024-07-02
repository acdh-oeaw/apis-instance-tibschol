# Generated by Django 4.2.13 on 2024-07-02 09:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "apis_ontology",
            "0019_subject_alter_versionwork_subject_alter_work_subject_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="work",
            name="subject_vocab",
            field=models.ManyToManyField(
                blank=True, to="apis_ontology.subject", verbose_name="Subject"
            ),
        ),
    ]
