# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-03-21 18:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feeditem',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Project'),
        ),
    ]
