# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-06 10:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0029_auto_20171206_1925'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='post_manager',
            new_name='comment_post_intermediate',
        ),
    ]
