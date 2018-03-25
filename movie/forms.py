from django import forms

class MovieSearchForm(forms.Form):
    movie = forms.CharField(max_length=20)
