from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def testpost(request):
    if request.method == 'POST':
        print request
        return HttpResponse('test post')
    else:
        return HttpResponse('test')
