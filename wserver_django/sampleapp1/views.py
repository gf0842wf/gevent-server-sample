from django.shortcuts import render
from django.http import HttpResponse

import gevent

# Create your views here.

def sampleapp1_media(request, path):
    parent = os.path.abspath(os.path.dirname(__file__))
    root = os.path.join(parent, 'media')
    return django.views.static.serve(request, path, root)

def hello(request):
    if request.method == "GET":
        return HttpResponse("hello world")

def test_sleep(request):
    if request.method == "GET":
        gevent.sleep(5)
        return HttpResponse("test sleep")