# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-05 10:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0002_auto_20170629_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='expand_type',
            field=models.CharField(choices=[('read', 'Expand read'), ('r/n', 'Read and notes'), ('notes', 'Expand notes')], default='r/n', max_length=25),
        ),
    ]