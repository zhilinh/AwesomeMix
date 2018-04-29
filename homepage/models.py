from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
import os

# Create your models here.

def update_filename(instance, filename):
    path = "media/"
    format = instance.user.username + '.' + filename.split('.')[-1]
    return os.path.join(path, format)

class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    img = models.ImageField(upload_to=update_filename, blank=True)
    bio = models.TextField(default='')
    follower = models.ManyToManyField(User)

    movie_wish_list = models.TextField(default='[]')
    music_wish_list = models.TextField(default='[]')
    book_wish_list = models.TextField(default='[]')

    movie_watched = models.TextField(default='[]')
    music_played = models.TextField(default='[]')
    book_read = models.TextField(default='[]')

class ImageForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['img']

class BioForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['bio']