# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 13:47
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PGE', '0004_auto_20170716_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='work_type',
        ),
        migrations.AddField(
            model_name='session',
            name='task',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='PGE.Task'),
        ),
    ]
