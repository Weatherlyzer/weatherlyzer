# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-12 20:49
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20160412_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accuracy',
            name='length',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accuracies', to='base.Length'),
        ),
        migrations.AlterField(
            model_name='accuracy',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accuracies', to='base.Location'),
        ),
        migrations.AlterField(
            model_name='accuracy',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accuracies', to='base.Type'),
        ),
        migrations.AlterField(
            model_name='accuracy',
            name='value',
            field=models.FloatField(default=0),
        ),
    ]
