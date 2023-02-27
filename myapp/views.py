from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import redirect

def index(request):
    return HttpResponse("Welcome to our website!")

def profile(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return HttpResponse("You just logged in! Welcome admin!")
        else:
            return HttpResponse("You just logged in! Welcome student!")
    else:
        response = redirect('/accounts/login')
        return response
        #return HttpResponse("You are not logged in! ")