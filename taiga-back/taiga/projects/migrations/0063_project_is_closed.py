# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-30 09:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0062_auto_20181025_1207'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='is_closed',
            field=models.BooleanField(default=False, verbose_name='Is Closed'),
        ),
    ]
