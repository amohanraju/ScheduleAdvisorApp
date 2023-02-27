from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def index(request):
    return HttpResponse("Welcome to our website!")

def profile(request):
    template = loader.get_template('myapp/home.html')
    return HttpResponse(template.render({}, request))
    #return HttpResponse("YOU just logged in!")