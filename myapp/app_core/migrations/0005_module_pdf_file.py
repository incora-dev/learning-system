# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-12 11:38
from __future__ import unicode_literals

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_core', '0004_auto_20170710_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='pdf_file',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='PDF file'),
        ),
    ]
