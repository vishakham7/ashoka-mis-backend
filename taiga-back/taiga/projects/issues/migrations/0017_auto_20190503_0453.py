# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-05-03 04:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0016_auto_20190502_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='investigation_chainage_from',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Chainage From'),
        ),
        migrations.AddField(
            model_name='issue',
            name='investigation_chainage_side',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Chainage Side'),
        ),
        migrations.AddField(
            model_name='issue',
            name='investigation_chainage_to',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Chainage To'),
        ),
    ]
