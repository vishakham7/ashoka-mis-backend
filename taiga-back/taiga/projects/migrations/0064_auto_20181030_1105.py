# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-30 11:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0063_project_is_closed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='concession_period',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Scheduled End of Concession'),
        ),
    ]
