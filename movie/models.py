from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Person(models.Model):
    imdb_id = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    birth_year = models.CharField(max_length=4, blank=True)
    death_year = models.CharField(max_length=4, blank=True)
    primary_profession = models.CharField(max_length=50, blank=True)
    known_for_titles = models.CharField(max_length=100, blank=True)

class Movie(models.Model):
    imdb_id = models.CharField(max_length=10)
    directors = models.CharField(max_length=100, blank=True)
    writers = models.CharField(max_length=100, blank=True)
    casts = models.ManyToManyField(Person, related_name="acted_movies")
    pictures = models.TextField(blank=True)
    imdb_rating = models.DecimalField(decimal_places=1, max_digits=2)
    imdb_num_votes = models.IntegerField(default=0)

class MovieComment(models.Model):
    username = models.CharField(max_length=20)
    rate = models.IntegerField(default=0)
    comment = models.CharField(max_length=140, blank=True)
    likes = models.IntegerField(default=0)
    movie = models.ForeignKey(Movie)