from django import forms

class BookSearchForm(forms.Form):
    book = forms.CharField(max_length=140)
