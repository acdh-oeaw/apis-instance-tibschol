# Generated by Django 4.2.13 on 2024-07-02 20:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("apis_ontology", "0020_alter_work_subject_vocab"),
    ]

    operations = [
        migrations.AddField(
            model_name="persondirectpredecessorinlineageofperson",
            name="subject_of_teaching_vocab",
            field=models.ManyToManyField(
                blank=True,
                to="apis_ontology.subject",
                verbose_name="Subject of teaching",
            ),
        ),
        migrations.AddField(
            model_name="persondiscipleofperson",
            name="subject_of_teaching_vocab",
            field=models.ManyToManyField(
                blank=True,
                to="apis_ontology.subject",
                verbose_name="Subject of teaching",
            ),
        ),
        migrations.AddField(
            model_name="personreferswithnametotheviewsofperson",
            name="subject_of_teaching_vocab",
            field=models.ManyToManyField(
                blank=True,
                to="apis_ontology.subject",
                verbose_name="Subject of teaching",
            ),
        ),
        migrations.AddField(
            model_name="personreferswithoutnametotheviewsofperson",
            name="subject_of_teaching_vocab",
            field=models.ManyToManyField(
                blank=True,
                to="apis_ontology.subject",
                verbose_name="Subject of teaching",
            ),
        ),
        migrations.AddField(
            model_name="personrequestorofperson",
            name="subject_of_teaching_vocab",
            field=models.ManyToManyField(
                blank=True,
                to="apis_ontology.subject",
                verbose_name="Subject of teaching",
            ),
        ),
        migrations.AlterField(
            model_name="persondirectpredecessorinlineageofperson",
            name="subject_of_teaching",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
                verbose_name="subject of teaching",
            ),
        ),
        migrations.AlterField(
            model_name="persondiscipleofperson",
            name="subject_of_teaching",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
                verbose_name="subject of teaching",
            ),
        ),
        migrations.AlterField(
            model_name="personreferswithnametotheviewsofperson",
            name="subject_of_teaching",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
                verbose_name="subject of teaching",
            ),
        ),
        migrations.AlterField(
            model_name="personreferswithoutnametotheviewsofperson",
            name="subject_of_teaching",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
                verbose_name="subject of teaching",
            ),
        ),
        migrations.AlterField(
            model_name="personstudentofperson",
            name="subject_of_teaching",
            field=models.CharField(
                blank=True,
                editable=False,
                max_length=255,
                null=True,
                verbose_name="subject of teaching",
            ),
        ),
    ]