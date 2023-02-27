from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic

class IndexView(generic.ListView):
    template_name='myapp/index.html'
    def get_queryset(self):
        return
    #return HttpResponse("Welcome to our website!")

def profile(request):
    #template = loader.get_template('myapp/profile.html')
    #return HttpResponse(template.render({}, request))
    #return render(request, 'profile.html')
    return HttpResponse("YOU just logged in!")