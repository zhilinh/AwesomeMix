from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.

class MainView(TemplateView):
    template_name = 'movie/movie.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
