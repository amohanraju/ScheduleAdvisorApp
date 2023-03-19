from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
import requests

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
    
class CourseView(generic.ListView):
    template_name='myapp/courses.html'
    def get_queryset(self):
        return
    
# class SingleCourseView(generic.ListView):
#     template_name='myapp/single_course.html'
#     def get_queryset(self):
#         return

def api_data(request):
    if request.method == 'GET':
        class_dept = request.GET.get('classes')
        url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.' \
                'IScript_ClassSearch?institution=UVA01&term=1228&subject={class_dept}&page=1'
        response = requests.get(url).json()
        return render(request, 'myapp/courses.html', {'class_data' : response})
    else:
        return HttpResponseRedirect('accounts/profile/browse_courses')