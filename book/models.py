from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User

# Create your models here.

class Book(models.Model):
    google_id = models.CharField(max_length=140, primary_key=True)
    all_rates = models.DecimalField(max_digits=30, decimal_places=1)
    rater_num = models.IntegerField(default=0)
    cover_path = models.TextField(default="[]")

class BookComment(models.Model):
    user = models.ForeignKey(User, related_name="book_comments")
    rate = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    comment = models.CharField(max_length=140, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    book_id = models.CharField(max_length=140)

class BookCommentForm(ModelForm):
    class Meta:
        model = BookComment
        fields = ['comment']