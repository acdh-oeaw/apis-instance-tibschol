# Generated by Django 4.2.14 on 2024-07-16 05:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0025_alter_instanceiscopiedfrominstance_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="instance",
            name="dimension",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="WxH size in cm"
            ),
        ),
        migrations.AddField(
            model_name="versioninstance",
            name="dimension",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="WxH size in cm"
            ),
        ),
    ]
