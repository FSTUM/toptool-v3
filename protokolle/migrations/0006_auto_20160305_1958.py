# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-05 18:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import protokolle.models


class Migration(migrations.Migration):

    dependencies = [
        ('protokolle', '0005_auto_20160305_0246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='protokoll',
            name='approved',
            field=models.BooleanField(verbose_name='genehmigt'),
        ),
        migrations.AlterField(
            model_name='protokoll',
            name='begin',
            field=models.TimeField(verbose_name='Beginn der Sitzung'),
        ),
        migrations.AlterField(
            model_name='protokoll',
            name='end',
            field=models.TimeField(verbose_name='Ende der Sitzung'),
        ),
        migrations.AlterField(
            model_name='protokoll',
            name='meeting',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='meetings.Meeting', verbose_name='Sitzung'),
        ),
        migrations.AlterField(
            model_name='protokoll',
            name='t2t',
            field=models.FileField(upload_to=protokolle.models.protokoll_path, verbose_name='Protokoll'),
        ),
        migrations.AlterField(
            model_name='protokoll',
            name='version',
            field=models.DateTimeField(auto_now=True, verbose_name='Version'),
        ),
    ]