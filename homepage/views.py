from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.views.generic.base import TemplateView
from django.http import HttpResponse, Http404
from django.core import serializers
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from .forms import RegistrationForm
from .models import Profile, Movie
import json

# Create your views here.

class MainView(TemplateView):
    template_name = 'homepage/homepage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class ProfileView(TemplateView):
    template_name = 'homepage/profile.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if not request.user.is_authenticated():
            return Http404

        user_profile = request.user.user_profile
        movie_watchlist = json.loads(user_profile.movie_wish_list)
        context['movie_watchlist'] = []
        for tmdb_id in movie_watchlist:
            movie = Movie.objects.get(pk=tmdb_id)
            context['movie_watchlist'].append({'id': tmdb_id, 'poster_path': movie.poster_path})

        movie_watched = json.loads(user_profile.movie_watched)
        context['movie_watched'] = []
        for tmdb_id in movie_watched:
            movie = Movie.objects.get(pk=tmdb_id)
            context['movie_watched'].append({'id': tmdb_id, 'poster_path': movie.poster_path})

        return self.render_to_response(context)

@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'homepage/register.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'homepage/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        )
    new_user.is_active = False
    new_user.save()
    new_profile = Profile(user=new_user)
    new_profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
    Please click the link below to verify your email address and
    complete the registration of your account:

      http://{host}{path}
    """.format(host=request.get_host(),
               path=reverse('homepage:confirmed', args=(new_user.username, token)))

    send_mail(subject="Awesome Mix - Verify your email address",
              message=email_body,
              from_email="zhilinh@andrew.cmu.edu",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']
    return render(request, 'homepage/confirming.html', context)

@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()

    login(request, user)
    return render(request, 'homepage/confirmed.html', {})
