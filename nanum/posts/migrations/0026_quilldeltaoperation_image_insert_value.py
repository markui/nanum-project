# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-05 07:16
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0025_auto_20171205_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='quilldeltaoperation',
            name='image_insert_value',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
