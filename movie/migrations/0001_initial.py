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
            name='Movie',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imdb_id', models.CharField(blank=True, max_length=10)),
                ('pictures', models.TextField(blank=True)),
                ('imdb_rating', models.DecimalField(decimal_places=1, max_digits=2)),
                ('imdb_num_votes', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='MovieComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=20)),
                ('rate', models.IntegerField(default=0)),
                ('comment', models.CharField(blank=True, max_length=140)),
                ('likes', models.IntegerField(default=0)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='movie.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imdb_id', models.CharField(blank=True, max_length=10)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('birth_year', models.IntegerField(default=0)),
                ('death_year', models.IntegerField(default=0)),
                ('primary_profession', models.CharField(blank=True, max_length=50)),
                ('known_for_titles', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='movie',
            name='casts',
            field=models.ManyToManyField(related_name='acted_movies', to='movie.Person'),
        ),
        migrations.AddField(
            model_name='movie',
            name='director',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='directed_movies', to='movie.Person'),
        ),
        migrations.AddField(
            model_name='movie',
            name='writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='written_movies', to='movie.Person'),
        ),
    ]