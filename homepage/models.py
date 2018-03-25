from django.db import models
from django.contrib.auth.models import User
from movie.models import MovieComment
from music.models import MusicComment

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    img = models.ImageField(upload_to='media/', blank=True)
    bio = models.CharField(max_length=140, blank=True)
    follower = models.ManyToManyField(User)
    movie_wish_list = models.TextField(blank=True)
    music_wish_list = models.TextField(blank=True)
    book_wish_list = models.TextField(blank=True)
    movie_watched = models.TextField(blank=True)
    music_listened = models.TextField(blank=True)
    book_read = models.TextField(blank=True)
    movie_comments = models.ForeignKey(MovieComment, related_name='movie_commenter')
    music_comments = models.ForeignKey(MusicComment, related_name='music_commenter')
    liked_movie_comments = models.ForeignKey(MovieComment, related_name='movie_liker')
    liked_music_comments = models.ForeignKey(MusicComment, related_name='music_liker')
