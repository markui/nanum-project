# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-28 10:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_question_topics'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='images',
            name='question',
        ),
        migrations.DeleteModel(
            name='Images',
        ),
    ]
