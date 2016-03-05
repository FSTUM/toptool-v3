# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-03 10:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0007_remove_meeting_attendees'),
        ('persons', '0002_auto_20160301_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='function',
            name='plural',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='person',
            name='version',
            field=models.DateTimeField(auto_now=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='attendant',
            name='functions',
            field=models.ManyToManyField(blank=True, to='persons.Function'),
        ),
        migrations.AddField(
            model_name='attendant',
            name='meeting',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meetings.Meeting'),
        ),
        migrations.AddField(
            model_name='attendant',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persons.Person'),
        ),
    ]