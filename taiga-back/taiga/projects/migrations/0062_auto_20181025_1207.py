# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-25 12:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0061_auto_20181023_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='O_M_handover_date',
            field=models.DateField(blank=True, null=True, verbose_name='O & M handover date'),
        ),
        migrations.AddField(
            model_name='project',
            name='appointed_date',
            field=models.DateField(blank=True, null=True, verbose_name='Appointed Date O & M Handover Date'),
        ),
        migrations.AddField(
            model_name='project',
            name='authority',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Autority'),
        ),
        migrations.AddField(
            model_name='project',
            name='concession_period',
            field=models.DateField(blank=True, max_length=200, null=True, verbose_name='Scheduled End of Concession'),
        ),
        migrations.AddField(
            model_name='project',
            name='concessionaire',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Concessionaire'),
        ),
        migrations.AddField(
            model_name='project',
            name='date_of_signing_of_concession_agreement',
            field=models.DateField(blank=True, null=True, verbose_name='Date of signing of Concession Agreement'),
        ),
        migrations.AddField(
            model_name='project',
            name='epc_contractor',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='EPC Contractor'),
        ),
        migrations.AddField(
            model_name='project',
            name='independent_consultant_during_O_and_M_period',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='Independent Consultant during O & M period'),
        ),
        migrations.AddField(
            model_name='project',
            name='package_no',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Package No'),
        ),
        migrations.AddField(
            model_name='project',
            name='scheduled_end_of_concession',
            field=models.DateField(blank=True, null=True, verbose_name='Scheduled End of Concession'),
        ),
        migrations.AddField(
            model_name='project',
            name='start_and_end_chainage',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Start and End Chainage'),
        ),
    ]
