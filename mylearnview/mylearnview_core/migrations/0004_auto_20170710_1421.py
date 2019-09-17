# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-10 14:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mylearnview_core', '0003_page_custom_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='opened',
            field=models.BooleanField(default=False, verbose_name='Opened page'),
        ),
        migrations.AlterField(
            model_name='page',
            name='sort_index',
            field=models.IntegerField(verbose_name='Sort index'),
        ),
        migrations.AlterField(
            model_name='studentpagenote',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Student'),
        ),
    ]
