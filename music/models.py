from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

# Create your models here.

class Music(models.Model):
    spotify_id = models.CharField(max_length=140, primary_key=True)
    all_rates = models.DecimalField(max_digits=30, decimal_places=1)
    rater_num = models.IntegerField(default=0)
    cover_path = models.TextField(default="[]")

class MusicComment(models.Model):
    user = models.ForeignKey(User, related_name="music_comments")
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    comment = models.CharField(max_length=140, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    music_id = models.CharField(max_length=140)

class MusicCommentForm(ModelForm):
    class Meta:
        model = MusicComment
        fields = ['comment']