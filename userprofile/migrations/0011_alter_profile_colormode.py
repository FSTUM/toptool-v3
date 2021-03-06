# Generated by Django 4.0 on 2021-12-16 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0010_profile_colormode"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="colormode",
            field=models.CharField(
                blank=True,
                choices=[("default", "Systemstandard (Standard)"), ("light", "Hell"), ("dark", "Dunkel")],
                default="default",
                max_length=30,
                verbose_name="Farbschema",
            ),
        ),
    ]
