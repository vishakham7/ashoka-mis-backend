# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-02-16 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0014_issue_compliance_is_update'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='compliance_description',
            field=models.TextField(blank=True, null=True, verbose_name='compliance description'),
        ),
    ]
