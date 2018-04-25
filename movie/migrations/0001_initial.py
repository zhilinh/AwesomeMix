# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-04-25 01:15
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('tmdb_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('all_rates', models.DecimalField(decimal_places=1, max_digits=30)),
                ('rater_num', models.IntegerField(default=0)),
                ('poster_path', models.CharField(max_length=140)),
            ],
        ),
        migrations.CreateModel(
            name='MovieComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=1, max_digits=2)),
                ('comment', models.CharField(blank=True, max_length=140)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('likes', models.IntegerField(default=0)),
                ('movie_id', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
