from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
import decimal
import requests
import json
import os
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from .forms import MusicSearchForm
from .models import Music, MusicComment
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
        return self.render_to_response(context)

def search(request):
    context = {}
    form = MusicSearchForm(request.GET)
    if form.is_valid():
        results = spotify.search(q='artist:' + request.GET['music'], type='artist')
        items = results['artists']['items']
        context['artists'] = []
        for artist in items:
            if len(artist['images']) > 1 and artist['images'][2]['height'] == 160 and artist['images'][2]['width'] == 160:
                context['artists'].append({'name': artist['name'], 'image': artist['images'][2]['url']})
        return render(request, 'music/search_result.html', context)
    else:
        return Http404
