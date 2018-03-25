from django.shortcuts import render
from django.views.generic.base import TemplateView
import tmdbsimple as tmdb
import requests
import json

from .forms import MovieSearchForm

API_KEY = "b0fac58f78c60eb1ca0776a25185aef0"
url = "https://api.themoviedb.org/3/search/movie"

# Create your views here.

class MainView(TemplateView):
    template_name = 'movie/homepage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_form = MovieSearchForm(self.request.GET or None)
        context['search_form'] = search_form
        return self.render_to_response(context)


class MovieView(TemplateView):
    template_name = 'movie/movie.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


def search(request):
    context = {}
    form = MovieSearchForm(request.GET)
    if form.is_valid():
        movie_name = form.cleaned_data['movie']
        payload = { 'api_key': API_KEY, 'language': 'en-US', 'query': movie_name, 'page': 1, 'include_adult': False }
        response = requests.get(url, params=payload)
        context = response.json()
    return render(request, 'movie/search_result.html', context)
