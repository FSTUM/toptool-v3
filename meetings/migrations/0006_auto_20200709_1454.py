# Generated by Django 2.2.14 on 2020-07-09 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meetings", "0005_auto_20180218_1021"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meeting",
            name="title",
            field=models.CharField(
                blank=True,
                help_text="Wenn kein Titel gesetzt ist, wird der Standardsitzungstitel verwendet.",
                max_length=200,
                verbose_name="Alternativer Titel",
            ),
        ),
    ]
