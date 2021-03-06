# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-12 17:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20160412_0848'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timerange',
            old_name='parent_id',
            new_name='parent',
        ),
        migrations.AddField(
            model_name='statistics',
            name='min',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='avg',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='statistics',
            name='max',
            field=models.FloatField(default=0),
        ),
    ]
