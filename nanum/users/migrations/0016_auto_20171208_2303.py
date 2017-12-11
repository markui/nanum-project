# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-08 14:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_auto_20171208_1828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='educationcredential',
            name='user',
        ),
        migrations.RemoveField(
            model_name='employmentcredential',
            name='user',
        ),
        migrations.AddField(
            model_name='educationcredential',
            name='profile',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='education_credentials', to='users.Profile'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employmentcredential',
            name='profile',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, related_name='employment_credentials', to='users.Profile'),
            preserve_default=False,
        ),
    ]
