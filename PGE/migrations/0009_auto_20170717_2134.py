# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-17 16:04
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('PGE', '0008_auto_20170717_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='start_date_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 17, 16, 4, 56, 699267, tzinfo=utc)),
        ),
    ]
