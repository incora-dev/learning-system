# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-06 11:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='page_number',
            new_name='sort_index',
        ),
        migrations.RemoveField(
            model_name='module',
            name='pdf_file',
        ),
        migrations.AddField(
            model_name='page',
            name='pagetype',
            field=models.CharField(blank=True, choices=[('image', 'Image'), ('custom', 'Custom')], max_length=25),
        ),
        migrations.AlterField(
            model_name='course',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='image_file_reference',
            field=models.CharField(blank=True, max_length=256, verbose_name='Reference to image'),
        ),
        migrations.AlterField(
            model_name='studentpagenote',
            name='created_datetime',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]