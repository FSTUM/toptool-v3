# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-09-10 12:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetingtypes', '0002_auto_20170315_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingtype',
            name='first_topid',
            field=models.IntegerField(default=1, verbose_name='Nummer des ersten TOPs'),
        ),
    ]