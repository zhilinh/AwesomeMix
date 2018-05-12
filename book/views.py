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

from .forms import BookSearchForm
from .models import Book, BookComment, BookCommentForm
from configparser import ConfigParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
config.read(os.path.join(BASE_DIR, 'config.ini'))

NYT_API_KEY = config.get("New_York_Times", "NYT_API_KEY")
GOOGLE_API_KEY = config.get("Google", "GOOGLE_API_KEY")


# Create your views here.

class MainView(TemplateView):
    template_name = 'book/homepage.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        search_form = BookSearchForm(self.request.GET or None)

        payload = {'list': 'combined-print-and-e-book-fiction', 'api-key': NYT_API_KEY}
        url = "https://api.nytimes.com/svc/books/v3/lists.json"
        google_url = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
        response = requests.get(url, params=payload)
        results = response.json()['results']
        context['best_sellers'] = []

        for book in results:
            payload = {'key': GOOGLE_API_KEY}
            url = google_url + book['book_details'][0]['primary_isbn13']
            response = requests.get(url, params=payload).json()
            if response['totalItems'] != 0:
                result = response['items'][0]
            # else:
            #     print(book['book_details'][0])
                context['best_sellers'].append(result)

        context['search_form'] = search_form
        return self.render_to_response(context)

class BookView(TemplateView):
    template_name = 'book/book.html'

    def get_user_info(self, request, result):
        result['wishlist'] = True
        if request.user.is_authenticated():
            # User wishlist
            user_profile = request.user.user_profile
            book_list = json.loads(user_profile.book_wish_list)
            if result['id'] in book_list:
                result['wishlist'] = False
            # User rate
            try:
                user_comment = BookComment.objects.get(book_id=result['id'], user=request.user)
                result['user_comment'] = user_comment
            except:
                result['user_comment'] = {'rate': 0}

    def get_rate(self, result):
        try:
            book = Book.objects.get(pk=result['id'])
        except:
            book = Book(google_id=result['id'],
                        cover_path=result['volumeInfo']['imageLinks'],
                        all_rates=0,
                        rater_num=0)
            book.save()
        if book.rater_num == 0:
            result['avg_rate'] = 0
        else:
            result['avg_rate'] = "%.1f" % (book.all_rates * 2 / book.rater_num)
        result['rater_num'] = book.rater_num

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        bookid = context['bookid']

        payload = {'key': GOOGLE_API_KEY}
        url = "https://www.googleapis.com/books/v1/volumes/" + bookid
        response = requests.get(url, params=payload)
        context = response.json()
        if "error" in context:
            raise Http404
        context['id'] = bookid

        self.get_user_info(request, context)
        self.get_rate(context)
        return self.render_to_response(context)

    @method_decorator(transaction.atomic)
    def post(self, request, bookid):
        comment_form = BookCommentForm(request.POST)
        if not request.user.is_authenticated():
            return redirect('book:book', bookid=bookid)
        if not comment_form.is_valid():
            return redirect('book:book', bookid=bookid)

        user_profile = request.user.user_profile
        try:
            comment = BookComment.objects.get(book_id=bookid, user=request.user)
        except:
            comment = BookComment(book_id=bookid, user=request.user, rate=0)
        comment.comment = request.POST['comment']
        comment.save()
        reading_list = set(json.loads(user_profile.book_read))
        reading_list.add(bookid)
        user_profile.book_read = json.dumps(list(reading_list))
        user_profile.save()
        return redirect('book:book', bookid=bookid)

def search(request):
    context = {}
    form = BookSearchForm(request.GET)
    if form.is_valid():
        payload = {'key': GOOGLE_API_KEY}
        url = "https://www.googleapis.com/books/v1/volumes?q=" + request.GET['book']
        # payload = {'intitle': '', 'inauthor': '', 'inpublisher': '', 'subject': '', 'isbn': '', 'lccn': '', 'oclc': ''}
        response = requests.get(url, params=payload)
        results = response.json()
        return render(request, 'book/search_result.html', results)
    else:
        raise Http404

@transaction.atomic
def wishlist_op(request):
    if request.method != "POST" or 'bookId' not in request.POST:
        raise Http404
    if not request.user.is_authenticated():
        message = 'Please login first to add it to your wishlist.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile

    book = Book.objects.get(pk=request.POST['bookId'])
    book_list = set(json.loads(user_profile.book_wish_list))
    if int(request.POST['op']) == 1:
        book_list.add(book.google_id)
    else:
        book_list.remove(book.google_id)
    user_profile.book_wish_list = json.dumps(list(book_list))
    user_profile.save()

    return HttpResponse(context, content_type='application/json')

@transaction.atomic
def rate(request):
    if request.method != "POST" or 'bookId' not in request.POST or 'rating' not in request.POST:
        raise Http404
    if not request.user.is_authenticated():
        message = 'Please login first to make ratings and comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    context = {}
    user_profile = request.user.user_profile

    try:
        comment = BookComment.objects.get(book_id=request.POST['bookId'],
                                           user=request.user)
    except:
        comment = BookComment(book_id=request.POST['bookId'], user=request.user)
    book = Book.objects.get(google_id=request.POST['bookId'])
    book.all_rates = book.all_rates - comment.rate + decimal.Decimal(request.POST['rating'])
    if comment.rate == 0:
        book.rater_num = book.rater_num + 1
    comment.rate = request.POST['rating']
    book.save()
    comment.save()

    reading_list = set(json.loads(user_profile.book_read))
    reading_list.add(book.google_id)
    user_profile.book_read = json.dumps(list(reading_list))
    user_profile.save()

    return HttpResponse(context, content_type='application/json')

@transaction.atomic
def delete_comment(request):
    if request.method != "POST" or 'bookId' not in request.POST:
        raise Http404
    if not request.user.is_authenticated():
        message = 'Please login first to modify your comments.'
        json_error = '{ "error": "' + message + '" }'
        return HttpResponse(json_error, content_type='application/json')

    try:
        book = Book.objects.get(pk=request.POST['bookId'])
        comment = BookComment.objects.get(book_id=request.POST['bookId'], user=request.user)
        book.rater_num = book.rater_num - 1
        book.all_rates = book.all_rates - comment.rate
        book.save()
        comment.delete()

        user_profile = request.user.user_profile
        reading_list = json.loads(user_profile.book_read)
        # book_id as string!
        reading_list.remove(request.POST['bookId'])
        user_profile.book_read = json.dumps(list(reading_list))
        user_profile.save()
    except:
        pass
    # IMPORTANT: response json format!!
    return HttpResponse(json.dumps([]), content_type='application/json')

def read_comment(request, bookid):
    context = {}
    book = Book.objects.get(pk=bookid)

    payload = {'key': GOOGLE_API_KEY}
    url = "https://www.googleapis.com/books/v1/volumes/" + bookid
    response = requests.get(url, params=payload)
    result = response.json()

    context['title'] = result['volumeInfo']['title']
    context['cover_path'] = ast.literal_eval(book.cover_path)
    context['published_year'] = result['volumeInfo']['publishedDate'].split('-')[0]

    comments = BookComment.objects.filter(book_id=bookid).exclude(comment="")
    context['user_comments'] = comments
    context['id'] = bookid

    return render(request, 'book/book_comment.html', context)
