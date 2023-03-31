from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from myapp.models import Course
from django.urls import reverse
import requests
import datetime
import re

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

class CalendarObj():
    def __init__(self, course):
        self.course_mnemonic = course.course_mnemonic
        self.course_catalog_nbr = course.course_catalog_nbr
        self.course_id = self.course_mnemonic + " " + self.course_catalog_nbr
        self.course_days_of_week = course.course_days_of_week
        self.course_subject = course.course_subject
        self.course_start_time = course.course_start_time
        self.course_end_time = course.course_end_time
        self.coursenum = ""
        self.start_tag, self.end_tag = self.populate_tags() 
    
    def populate_tags(self):
        start_tag = str(self.course_start_time)[0:2] + "_" + str(self.course_start_time)[3:5]
        end_tag = str(self.course_end_time)[0:2] + "_" + str(self.course_end_time)[3:5]
        if start_tag[0] == '0':
            start_tag = start_tag[1:]
        if end_tag[0] == '0':
            end_tag = end_tag[1:]
        
        return start_tag, end_tag

def api_data(request):
    if request.method == 'GET':
        class_dept = request.GET.get("classes")
        url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.' \
                'IScript_ClassSearch?institution=UVA01&term=1232&subject=%s&page=1' % class_dept
        classes = requests.get(url).json()
        #return HttpResponse(url)
        class_objects = []
        if(len(classes) > 0):
            for course in classes:
                if(not Course.objects.filter(course_id= course.get("crse_id"), course_section= course.get("class_section"), course_catalog_nbr=course.get("catalog_nbr"), course_instructor = course.get("instructors")[0]['name']).exists()):
                    start = course.get("meetings")[0]['start_time']
                    if (start != ""):
                        start = datetime.datetime.strptime(course.get("meetings")[0]['start_time'], '%H.%M.%S.%f%z').strftime('%I:%M %p')
                    end = course.get("meetings")[0]['end_time']
                    if (end != ""):
                        end = datetime.datetime.strptime(course.get("meetings")[0]['end_time'], '%H.%M.%S.%f%z').strftime('%I:%M %p')
                    
                    course_model_instance = Course(
                        course_id = course.get('crse_id'),
                        course_section = course.get('class_section'),
                        course_catalog_nbr = course.get('catalog_nbr'),

                        course_subject = course.get('descr'),
                        course_mnemonic = course.get('subject'),

                        course_instructor = course.get("instructors")[0]['name'],
                        course_location = course.get("meetings")[0]['facility_descr'],

                        course_size = course.get('class_capacity'),
                        course_enrollment_total = course.get('enrollment_total'),
                        course_enrollment_availability = course.get('enrollment_available'),
                        course_waitlist_total = course.get('wait_tot'),
                        course_waitlist_cap = course.get('wait_cap'),

                        course_days_of_week = course.get("meetings")[0]['days'],
                        course_start_time = start,
                        course_end_time = end,

                    )

                    course_model_instance.save()
                    course_model_instance.course_added_to_cart.set([])
                    course_model_instance.save()

                #For updating info if users join / get off waitlist and as enrollment size changes
                specific_course = Course.objects.get(course_id= course.get("crse_id"), course_section= course.get("class_section"), course_catalog_nbr=course.get("catalog_nbr"), course_instructor = course.get("instructors")[0]['name'])    
                if(specific_course.course_enrollment_total != course.get('enrollment_total') or 
                   specific_course.course_enrollment_availability != course.get('enrollment_available') or
                   specific_course.course_waitlist_total != course.get('wait_tot') or 
                   specific_course.course_waitlist_cap != course.get('wait_cap')):
                        specific_course.course_enrollment_total = course.get('enrollment_total'),
                        specific_course.course_enrollment_availability = course.get('enrollment_available') ,
                        specific_course.course_waitlist_total = course.get('wait_tot'),
                        specific_course.course_waitlist_cap = course.get('wait_cap'),
                        specific_course.save()
                class_objects.append(specific_course)
        #primary_keys = [instance.pk for instance in class_objects]

        finalList = zip(class_objects, classes)
        context = {'content': finalList}
        return render(request, 'myapp/courses.html', context)
        #return render(request, 'myapp/courses.html', {'classes' : classes, 'primary_keys' : primary_keys})
    else:
        return HttpResponseRedirect('accounts/profile/browse_courses')
    

def shoppingCart(request):
    if(request.user.is_authenticated):  
        current_user = request.user
        all_courses = Course.objects.all()
        courses_in_cart = []
        courses_in_cart = Course.objects.filter(course_added_to_cart = current_user)
        return render(request, 'myapp/shoppingCart.html', {'courses_in_cart': courses_in_cart,})
    else:
        response = redirect('/accounts/login')
        return response



def addToCart(request, pk):
    if(request.user.is_authenticated):  
        #https://www.youtube.com/watch?v=PXqRPqDjDgc
        course = get_object_or_404(Course, pk = pk)
        course.course_added_to_cart.add(request.user)
        course.save()
        return shoppingCart(request)
    else:
        response = redirect('/accounts/login')
        return response

def removeFromCart(request, pk):
    #Get user from route and then remove the associated course and save
    course = get_object_or_404(Course, pk = pk)
    course.course_added_to_cart.remove(request.user)
    course.save()
    return shoppingCart(request)

def calendar(request):
    # template = loader.get_template('myapp/calendar.html')
    # return HttpResponse(template.render({}, request))

    if(request.user.is_authenticated):  
        current_user = request.user
        courses_in_cart = Course.objects.filter(course_added_to_cart = current_user)
        calendar_courses = []
        seen_classes = set()
        for i in range(len(courses_in_cart)):
            course = courses_in_cart[i]
            calendar_course = (CalendarObj(course))
            if calendar_course.course_id not in seen_classes:
                seen_classes.add(calendar_course.course_id)
                calendar_course.coursenum = i
            calendar_courses.append(calendar_course)
        mon,tue,wed,thu,fri=[],[],[],[],[]
        for course in calendar_courses:
            if "Mo" in course.course_days_of_week:
                mon.append(course)
            if "Tu" in course.course_days_of_week:
                tue.append(course)
            if "We" in course.course_days_of_week:
                wed.append(course)
            if "Th" in course.course_days_of_week:
                thu.append(course)
            if "Fr" in course.course_days_of_week:
                fri.append(course)
        week = [mon, tue, wed, thu, fri]
        for i in range(len(week)):
            week[i] = sorted(week[i], key=lambda obj: obj.start_tag)
        week_dict = {"MON" : week[0], "TUE" : week[1], "WED" : week[2], "THU" : week[3], "FRI" : week[4]} 
        return render(request, 'myapp/calendar.html', {'week' : week_dict, 'schedule' : week})
    else:
        response = redirect('/accounts/login')
        return response