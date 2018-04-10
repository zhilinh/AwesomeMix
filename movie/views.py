from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import tmdbsimple as tmdb
import requests
import json
import os
import time

from .forms import MovieSearchForm
from .models import Movie, MovieComment
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

TMDB_API_KEY = config.get("API_KEY", "TMDB_API_KEY")
GRACENOTE_API_KEY = config.get("API_KEY", "GRACENOTE_API_KEY")

# Create your views here.

class MainView(TemplateView):
    template_name = 'movie/homepage.html'

    def process_request(self, request):
        try:
            real_ip = request.META['HTTP_X_FORWARDED_FOR']
        except KeyError:
            return None
        else:
            # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs. The
            # client's IP will be the first one.
            real_ip = real_ip.split(",")[0].strip()
        return real_ip

    def getZIP(self, request):
        ip = self.process_request(request)
        if ip == None:
            ip = '127.0.0.1'
        freegeoip_url = "https://freegeoip.net/json/" + ip
        response = requests.get(freegeoip_url)
        geo_info = response.json()
        zip_code = geo_info['zip_code']
        if len(zip_code) == 0:
            zip_code = '15213'
        return zip_code

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_form = MovieSearchForm(self.request.GET or None)
        zip_code = self.getZIP(request)
        now_showing_url = "http://data.tmsapi.com/v1.1/movies/showings"
        payload = { "startDate": time.strftime("%Y-%m-%d"), "zip": zip_code, "api_key": GRACENOTE_API_KEY}
        response = requests.get(now_showing_url, params=payload)
        context['search_form'] = search_form
        context['api_key'] = GRACENOTE_API_KEY
        context['hits'] = []
        for i in range(10):
            context['hits'].append(response.json()[i])
        return self.render_to_response(context)

class MovieView(TemplateView):
    template_name = 'movie/movie.html'

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        payload = { 'api_key': TMDB_API_KEY, 'language': 'en-US', 'append_to_response': 'credits,videos'}
        url = "https://api.themoviedb.org/3/movie/" + context['movieid']
        response = requests.get(url, params=payload)
        result = response.json()
        # Retrieve credits of the movie
        credits_all = result['credits']
        credits = { 'cast': [], 'directors': [], 'writers': [], 'top_cast': []}
        # Retrieve directors and writers
        for crew in credits_all['crew']:
            if crew['job'] == 'Director':
                credits['directors'].append(crew)
            elif crew['department'] == 'Writing':
                credits['writers'].append(crew)
        # Retrieve the top 5 and 10 casts
        for i in range(10):
            if i >= len(credits_all['cast']):
                break
            if i < 5:
                credits['top_cast'].append(credits_all['cast'][i])
            credits['cast'].append(credits_all['cast'][i])
        # Replace the origin credits to simplified credits
        result['credits'] = credits
        result['release_year'] = result['release_date'].split('-')[0]

        # Rearrange the videos
        videos = []
        count = 0
        videos_num = len(result['videos']['results'])
        for i in range(videos_num):
            if count > videos_num:
                break
            if count % 3 == 0:
                videos.append([])
            videos[count // 3].append(result['videos']['results'][count])
            count += 1
        result['videos'] = videos

        result['user_comment'] = {'rate': 0, 'wishlist': True}
        if request.user.is_authenticated():
            # User wishlist
            user_profile = request.user.user_profile
            movie_list = json.loads(user_profile.movie_wish_list)
            if result['id'] in movie_list:
                result['user_comment']['wishlist'] = False
            # User rate
            try:
                user_comment = MovieComment.objects.get(movie_id=result['id'], user=request.user)
                result['user_comment']['rate'] = user_comment.rate
            except:
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
    else:
        return Http404

@transaction.atomic
def rate(request):
    if request.method != "POST" or 'movieId' not in request.POST or 'rating' not in request.POST:
        return Http404
    if not request.user.is_authenticated():
        message = 'Please login first to make ratings and comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile
    try:
        movie = Movie.objects.get(tmdb_id=request.POST['movieId'])
        movie.all_rates = movie.all_rates + request.POST['rating']
        movie.rater_num = movie.rater_num + 1
    except:
        movie = Movie(tmdb_id=request.POST['movieId'],
                      all_rates=request.POST['rating'],
                      rater_num=1)
    movie.save()

    try:
        comment = MovieComment.objects.get(movie_id=request.POST['movieId'],
                                           user=request.user)
    except:
        comment = MovieComment(movie_id=request.POST['movieId'], user=request.user)
    comment.rate = request.POST['rating']
    comment.save()
    watched_list = json.loads(user_profile.movie_watched)
    watched_list.append(movie.tmdb_id)
    user_profile.movie_watched = json.dumps(watched_list)
    user_profile.save()

    return HttpResponse(context, content_type='application/json')

@transaction.atomic
def wishlist_op(request):
    if request.method != "POST" or 'movieId' not in request.POST:
        return Http404
    if not request.user.is_authenticated():
        message = 'Please login first to add it to your wishlist.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile
    try:
        movie = Movie.objects.get(tmdb_id=request.POST['movieId'])
    except:
        movie = Movie(tmdb_id=request.POST['movieId'], all_rates=0)
        movie.save()
    movie_list = json.loads(user_profile.movie_wish_list)
    if int(request.POST['op']) == 1:
        movie_list.append(movie.tmdb_id)
    else:
        movie_list.remove(movie.tmdb_id)
    user_profile.movie_wish_list = json.dumps(movie_list)
    user_profile.save()

    return HttpResponse(context, content_type='application/json')
