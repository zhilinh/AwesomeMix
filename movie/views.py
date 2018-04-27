from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import tmdbsimple as tmdb
import decimal
import requests
import json
import os
import time

from .forms import MovieSearchForm
from .models import Movie, MovieComment, MovieCommentForm
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

TMDB_API_KEY = config.get("API_KEY", "TMDB_API_KEY")
GRACENOTE_API_KEY = config.get("API_KEY", "GRACENOTE_API_KEY")
tmdb.API_KEY = config.get("API_KEY", "TMDB_API_KEY")

NOW_PLAYING_MOVIES = {}

# Create your views here.

class MainView(TemplateView):
    template_name = 'movie/homepage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_form = MovieSearchForm(self.request.GET or None)
        zip_code = getZIP(request)
        now_showing_url = "http://data.tmsapi.com/v1.1/movies/showings"
        payload = { "startDate": time.strftime("%Y-%m-%d"), "zip": zip_code, "api_key": GRACENOTE_API_KEY}
        response = requests.get(now_showing_url, params=payload)
        NOW_PLAYING_MOVIES[zip_code] = response.json()

        context['search_form'] = search_form
        context['api_key'] = GRACENOTE_API_KEY
        context['hits'] = []
        search = tmdb.Search()
        for i in range(10):
            movie = response.json()[i]
            tmdb_response = search.movie(query=movie['title'],
                                         language='en-US',
                                         page=1,
                                         include_adult=False,
                                         year=time.struct_time.tm_year)
            if tmdb_response['total_results'] > 0:
                result = tmdb_response['results'][0]
                context['hits'].append({'id': result['id'],
                                        'title': movie['title'],
                                        'showtimes': movie['showtimes'],
                                        'ratings': movie['ratings'],
                                        'poster_path': result['poster_path']})
        return self.render_to_response(context)

class MovieView(TemplateView):
    template_name = 'movie/movie.html'

    def get_videos(self, result):
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
        return videos

    def get_credits(self, result):
        # Retrieve credits of the movie
        credits_all = result['credits']
        credits = {'cast': [], 'directors': [], 'writers': [], 'top_cast': []}
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
        return credits

    def get_user_info(self, request, result):
        result['wishlist'] = True
        if request.user.is_authenticated():
            # User wishlist
            user_profile = request.user.user_profile
            movie_list = json.loads(user_profile.movie_wish_list)
            if result['id'] in movie_list:
                result['wishlist'] = False
            # User rate
            try:
                user_comment = MovieComment.objects.get(movie_id=result['id'], user=request.user)
                result['user_comment'] = user_comment
            except:
                result['user_comment'] = {'rate': 0}

    def get_now_playing(self, result, request):
        # Get the theaters info for now playing movies
        showtimes = None
        zip_code = getZIP(request)
        if zip_code in NOW_PLAYING_MOVIES:
            for times in NOW_PLAYING_MOVIES[zip_code]:
                if times['title'] == result['title']:
                    showtimes = times['showtimes']
                    break

        if showtimes != None:
            theatres = {}
            for times in showtimes:
                if times['theatre']['id'] not in theatres:
                    theatres[times['theatre']['id']] = []
                info = {'dateTime': times['dateTime'].split('T')[1], 'theatre': times['theatre']['name']}
                if 'ticketURI' in times:
                    info['ticketURI'] = times['ticketURI']
                theatres[times['theatre']['id']].append(info)
            showtimes = theatres.values()
        return showtimes

    def get_similar_movies(self, result):
        similar_movies = []
        for i in range(6):
            similar_movies.append(result['similar_movies']['results'][i])
        return similar_movies

    def get_rate(self, result):
        try:
            movie = Movie.objects.get(pk=int(result['id']))
        except:
            movie = Movie(tmdb_id=int(result['id']),
                          poster_path=result['poster_path'],
                          all_rates=0,
                          rater_num=0)
            movie.save()
        if movie.rater_num == 0:
            result['avg_rate'] = 0
        else:
            result['avg_rate'] = movie.all_rates / movie.rater_num
        result['rater_num'] = movie.rater_num

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        comment_form = MovieCommentForm(self.request.GET or None)

        payload = { 'api_key': TMDB_API_KEY, 'language': 'en-US', 'append_to_response': 'credits,videos,similar_movies'}
        url = "https://api.themoviedb.org/3/movie/" + context['movieid']
        response = requests.get(url, params=payload)

        result = response.json()
        # Replace the origin credits to simplified credits
        result['credits'] = self.get_credits(result)
        result['videos'] = self.get_videos(result)
        result['release_year'] = result['release_date'].split('-')[0]
        result['showtimes'] = self.get_now_playing(result, request)
        result['comment_form'] = comment_form
        result['similar_movies'] = self.get_similar_movies(result)
        self.get_user_info(request, result)
        self.get_rate(result)
        return self.render_to_response(result)

    @method_decorator(transaction.atomic)
    def post(self, request, movieid):
        comment_form = MovieCommentForm(request.POST)
        if not request.user.is_authenticated():
            return redirect('movie:movie', movieid=movieid)
        if not comment_form.is_valid():
            return redirect('movie:movie', movieid=movieid)

        user_profile = request.user.user_profile
        try:
            comment = MovieComment.objects.get(movie_id=movieid, user=request.user)
        except:
            comment = MovieComment(movie_id=movieid, user=request.user, rate=0)
        comment.comment = request.POST['comment']
        comment.save()
        watched_list = set(json.loads(user_profile.movie_watched))
        watched_list.add(int(movieid))
        user_profile.movie_watched = json.dumps(list(watched_list))
        user_profile.save()
        return redirect('movie:movie', movieid=movieid)

def search(request):
    form = MovieSearchForm(request.GET)
    if form.is_valid():
        movie_name = form.cleaned_data['movie']
        search = tmdb.Search()
        response = search.movie(query=movie_name, language='en-US', page=1, include_adult=False)
        return render(request, 'movie/search_result.html', response)
    else:
        return Http404

@transaction.atomic
def rate(request):
    if request.method != "POST" or 'movieId' not in request.POST or 'rating' not in request.POST:
        raise Http404
    if not request.user.is_authenticated():
        message = 'Please login first to make ratings and comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile

    movie = Movie.objects.get(tmdb_id=request.POST['movieId'])
    movie.all_rates = movie.all_rates + decimal.Decimal(request.POST['rating'])
    movie.rater_num = movie.rater_num + 1
    movie.save()

    try:
        comment = MovieComment.objects.get(movie_id=request.POST['movieId'],
                                           user=request.user)
    except:
        comment = MovieComment(movie_id=request.POST['movieId'], user=request.user)
    comment.rate = request.POST['rating']
    comment.save()
    watched_list = set(json.loads(user_profile.movie_watched))
    watched_list.add(movie.tmdb_id)
    user_profile.movie_watched = json.dumps(list(watched_list))
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

    movie = Movie.objects.get(pk=request.POST['movieId'])
    movie_list = set(json.loads(user_profile.movie_wish_list))
    if int(request.POST['op']) == 1:
        movie_list.add(movie.tmdb_id)
    else:
        movie_list.remove(movie.tmdb_id)
    user_profile.movie_wish_list = json.dumps(list(movie_list))
    user_profile.save()

    return HttpResponse(context, content_type='application/json')

@transaction.atomic
def delete_comment(request):
    if request.method != "POST" or 'movieId' not in request.POST:
        return Http404
    if not request.user.is_authenticated():
        message = 'Please login first to modify your comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    try:
        comment = MovieComment.objects.get(movie_id=request.POST['movieId'], user=request.user)
        comment.delete()

        user_profile = request.user.user_profile
        watched_list = json.loads(user_profile.movie_watched)
        # movie_id as integer!
        watched_list.remove(int(request.POST['movieId']))
        user_profile.movie_watched = json.dumps(list(watched_list))
        user_profile.save()
    except:
        pass
    # IMPORTANT: response json format!!
    return HttpResponse(json.dumps([]), content_type='application/json')


def process_request(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
    except KeyError:
        return None
    else:
        # HTTP_X_FORWARDED_FOR can be a comma-separated list of IPs. The
        # client's IP will be the first one.
        real_ip = real_ip.split(",")[0].strip()
    return real_ip

def getZIP(request):
    ip = process_request(request)
    if ip == None:
        ip = '127.0.0.1'
    freegeoip_url = "https://freegeoip.net/json/" + ip
    response = requests.get(freegeoip_url)
    geo_info = response.json()
    zip_code = geo_info['zip_code']
    if len(zip_code) == 0:
        zip_code = '15213'
    return zip_code
