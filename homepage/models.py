from django.db import models
from django.contrib.auth.models import User
from movie.models import Movie, MovieComment
from music.models import MusicComment
from django.forms import ModelForm

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    img = models.ImageField(upload_to='media/', blank=True)
    bio = models.TextField(default='')
    follower = models.ManyToManyField(User)

    movie_wish_list = models.TextField(default='[]')
    music_wish_list = models.TextField(default='[]')
    book_wish_list = models.TextField(default='[]')

    movie_watched = models.TextField(default='[]')
    music_played = models.TextField(default='[]')
    book_read = models.TextField(default='[]')

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['img', 'bio']