from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to our website!")

def profile(request):
    return HttpResponse("YOU just logged in!")