from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MovieComment(models.Model):
    username = models.CharField(max_length=20)
    rate = models.IntegerField(default=0)
    comment = models.CharField(max_length=140, blank=True)
    likes = models.IntegerField(default=0)

class Movie(models.Model):
    query_id = models.CharField(max_length=140, blank=True)
    comments = models.ForeignKey(MovieComment, related_name="comments")
    picture = models.TextField(blank=True)
    all_rate = models.IntegerField(default=0)
    number_rater = models.IntegerField(default=0)