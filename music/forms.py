from django import forms

class MusicSearchForm(forms.Form):
    music = forms.CharField(max_length=140)
