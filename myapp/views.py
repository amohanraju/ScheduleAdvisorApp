from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.shortcuts import redirect

class IndexView(generic.ListView):
    template_name='myapp/index.html'
    def get_queryset(self):
        return

def profile(request):
    if request.user.is_authenticated:
        template = loader.get_template('myapp/profile.html')
        return HttpResponse(template.render({}, request))
    else:
        response = redirect('/accounts/login')
        return response