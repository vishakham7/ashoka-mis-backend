# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-21 10:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0011_auto_20181120_1437'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='target_date',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Target Date'),
        ),
    ]