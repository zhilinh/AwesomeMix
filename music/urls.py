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
from django.conf.urls import include, url

from . import views

app_name = 'music'
urlpatterns = [
    url(r'^$', views.MainView.as_view(), name='homepage'),
    url(r'^search_result', views.search, name='search'),
    url(r'^rate', views.rate, name='rate'),
    url(r'^wishlist_op', views.wishlist_op, name='wishlist_op'),
    url(r'^delete_comment', views.delete_comment, name='delete_comment'),
    url(r'^(?P<musicid>[a-zA-Z0-9]+)$', views.MusicView.as_view(), name='music'),
    url(r'^(?P<musicid>[a-zA-Z0-9]+)/comment', views.read_comment, name='read_comment')
]
