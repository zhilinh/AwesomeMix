# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-03-27 00:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Music',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_id', models.CharField(blank=True, max_length=140)),
                ('all_rate', models.IntegerField(default=0)),
                ('number_rater', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MusicComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('rate', models.IntegerField(default=0)),
                ('comment', models.CharField(blank=True, max_length=140)),
                ('likes', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='music',
            name='comments',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='music.MusicComment'),
        ),
    ]