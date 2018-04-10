"""awesomemix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'homepage'
urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='homepage'),
    url(r'^register$', views.register, name='register'),
    url(r'^confirm_registration/(?P<username>[a-zA-Z0-9]+)/(?P<token>[a-z0-9\-]+)$',
        views.confirm_registration, name='confirmed'),
    url(r'^profile/(?P<username>[a-zA-Z0-9]+)$', login_required(views.ProfileView.as_view()), name='profile'),
    # Route for built-in authentication with our own custom login page
    url(r'^login$', auth_views.login, {'template_name': 'homepage/login.html'}, name='login'),
    # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
]
