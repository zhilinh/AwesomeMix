from django.shortcuts import render
from django.views.generic.base import TemplateView
import tmdbsimple as tmdb
import requests
import json
import os
import time

from .forms import MovieSearchForm
from .models import Movie, Person
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

TMDB_API_KEY = config.get("API_KEY", "TMDB_API_KEY")
GRACENOTE_API_KEY = config.get("API_KEY", "GRACENOTE_API_KEY")

# Create your views here.

class MainView(TemplateView):
    template_name = 'movie/homepage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_form = MovieSearchForm(self.request.GET or None)
        # now_showing_url = "http://data.tmsapi.com/v1.1/movies/showings"
        # payload = { "startDate": time.strftime("%Y-%m-%d"), "zip": "15213", "api_key": GRACENOTE_API_KEY}
        # response = requests.get(now_showing_url, params=payload)
        context['search_form'] = search_form
        context['api_key'] = GRACENOTE_API_KEY
        # context['hits'] = []
        # for i in range(10):
        #     context['hits'].append(response.json()[i])
        return self.render_to_response(context)

class MovieView(TemplateView):
    template_name = 'movie/movie.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        payload = { 'api_key': TMDB_API_KEY, 'language': 'en-US'}
        url = "https://api.themoviedb.org/3/movie/" + context['movieid']
        response = requests.get(url, params=payload)
        result = response.json()
        try:
            directors = Movie.objects.get(imdb_id=result['imdb_id']).directors.split(',')
            writers = Movie.objects.get(imdb_id=result['imdb_id']).writers.split(',')
            result['directors'] = []
            result['writers'] = []
            for id in directors:
                result['directors'].append(Person.objects.get(imdb_id=id))
            for id in writers:
                result['writers'].append(Person.objects.get(imdb_id=id))
        except:
            print("No results")
            pass
        return self.render_to_response(result)

def search(request):
    context = {}
    form = MovieSearchForm(request.GET)
    if form.is_valid():
        movie_name = form.cleaned_data['movie']
        payload = { 'api_key': TMDB_API_KEY, 'language': 'en-US', 'query': movie_name, 'page': 1, 'include_adult': False}
        url = "https://api.themoviedb.org/3/search/movie"
        response = requests.get(url, params=payload)
        context = response.json()
    return render(request, 'movie/search_result.html', context)
