from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import decimal
import requests
import ast
import json
import os
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .forms import MusicSearchForm
from .models import Music, MusicComment, MusicCommentForm
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

CLIENT_ID = config.get("Spotify", "CLIENT_ID")
CLIENT_SECRET = config.get("Spotify", "CLIENT_SECRET")

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Create your views here.

class MainView(TemplateView):
    template_name = 'music/homepage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            results = spotify.new_releases(country='US')
        except:
            raise Http404
        return self.render_to_response(results)

class MusicView(TemplateView):
    template_name = 'music/music.html'

    def get_user_info(self, request, result):
        result['wishlist'] = True
        if request.user.is_authenticated():
            # User wishlist
            user_profile = request.user.user_profile
            music_list = json.loads(user_profile.music_wish_list)
            if result['id'] in music_list:
                result['wishlist'] = False
            # User rate
            try:
                user_comment = MusicComment.objects.get(music_id=result['id'], user=request.user)
                result['user_comment'] = user_comment
            except:
                result['user_comment'] = {'rate': 0}

    def get_rate(self, result):
        try:
            music = Music.objects.get(pk=result['id'])
        except:
            music = Music(spotify_id=result['id'],
                          cover_path=result['images'],
                          all_rates=0,
                          rater_num=0)
            music.save()
        if music.rater_num == 0:
            result['avg_rate'] = 0
        else:
            result['avg_rate'] = "%.1f" % (music.all_rates * 2 / music.rater_num)
        result['rater_num'] = music.rater_num

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            context = spotify.album(album_id=context['musicid'])
        except:
            raise Http404
        self.get_user_info(request, context)
        self.get_rate(context)
        return self.render_to_response(context)

    @method_decorator(transaction.atomic)
    def post(self, request, musicid):
        comment_form = MusicCommentForm(request.POST)
        if not request.user.is_authenticated():
            return redirect('music:music', musicid=musicid)
        if not comment_form.is_valid():
            return redirect('music:music', musicid=musicid)

        user_profile = request.user.user_profile
        try:
            comment = MusicComment.objects.get(music_id=musicid, user=request.user)
        except:
            comment = MusicComment(music_id=musicid, user=request.user, rate=0)
        comment.comment = request.POST['comment']
        comment.save()
        playlist = set(json.loads(user_profile.music_played))
        playlist.add(musicid)
        user_profile.music_played = json.dumps(list(playlist))
        user_profile.save()
        return redirect('music:music', musicid=musicid)

def search(request):
    context = {}
    form = MusicSearchForm(request.GET)
    if form.is_valid():
        results = spotify.search(q='album:' + request.GET['music'], type='album')
        return render(request, 'music/search_result.html', results)
    else:
        return Http404


@transaction.atomic
def wishlist_op(request):
    if request.method != "POST" or 'musicId' not in request.POST:
        return Http404
    if not request.user.is_authenticated():
        message = 'Please login first to add it to your wishlist.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile

    music = Music.objects.get(pk=request.POST['musicId'])
    music_list = set(json.loads(user_profile.music_wish_list))
    if int(request.POST['op']) == 1:
        music_list.add(music.spotify_id)
    else:
        music_list.remove(music.spotify_id)
    user_profile.music_wish_list = json.dumps(list(music_list))
    user_profile.save()

    return HttpResponse(context, content_type='application/json')

@transaction.atomic
def rate(request):
    if request.method != "POST" or 'musicId' not in request.POST or 'rating' not in request.POST:
        raise Http404
    if not request.user.is_authenticated():
        message = 'Please login first to make ratings and comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile

    music = Music.objects.get(spotify_id=request.POST['musicId'])
    music.all_rates = music.all_rates + decimal.Decimal(request.POST['rating'])
    music.rater_num = music.rater_num + 1
    music.save()

    try:
        comment = MusicComment.objects.get(music_id=request.POST['musicId'],
                                           user=request.user)
    except:
        comment = MusicComment(music_id=request.POST['musicId'], user=request.user)
    comment.rate = request.POST['rating']
    comment.save()
    playlist = set(json.loads(user_profile.music_played))
    playlist.add(music.spotify_id)
    user_profile.music_played = json.dumps(list(playlist))
    user_profile.save()

    return HttpResponse(context, content_type='application/json')

@transaction.atomic
def delete_comment(request):
    if request.method != "POST" or 'musicId' not in request.POST:
        return Http404
    if not request.user.is_authenticated():
        message = 'Please login first to modify your comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    try:
        music = Music.objects.get(pk=request.POST['movieId'])
        comment = MusicComment.objects.get(music_id=request.POST['musicId'], user=request.user)
        music.rater_num = music.rater_num - 1
        music.all_rates = music.all_rates - comment.rate
        music.save()
        comment.delete()

        user_profile = request.user.user_profile
        playlist = json.loads(user_profile.music_played)
        # music_id as string!
        playlist.remove(request.POST['musicId'])
        user_profile.music_played = json.dumps(list(playlist))
        user_profile.save()
    except:
        pass
    # IMPORTANT: response json format!!
    return HttpResponse(json.dumps([]), content_type='application/json')

def read_comment(request, musicid):
    context = {}
    music = Music.objects.get(pk=musicid)

    result = spotify.album(album_id=musicid)

    context['title'] = result['name']
    context['cover_path'] = ast.literal_eval(music.cover_path)[2]['url']
    context['release_year'] = result['release_date'].split('-')[0]

    comments = MusicComment.objects.filter(music_id=musicid)
    context['user_comments'] = comments
    context['id'] = musicid

    return render(request, 'music/music_comment.html', context)
