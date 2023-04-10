from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from myapp.models import Course, Schedule
from django.urls import reverse
import requests
import datetime
import re
import json

class IndexView(generic.ListView):
    template_name='myapp/index.html'
    def get_queryset(self):
        return

def profile(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            schedules = Schedule.objects.all().filter(isRejected=False, status = False)
            template = loader.get_template('myapp/adminHome.html')
            return HttpResponse(template.render({'schedules':schedules}, request))
        
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
        self.course_instructor = course.course_instructor
        self.course_location = course.course_location
        self.course_start_time = course.course_start_time
        self.course_end_time = course.course_end_time
        self.course_added_to_schedule = course.course_added_to_schedule
        self.course_added_to_cart = course.course_added_to_cart
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
        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
        return render(request, 'myapp/shoppingCart.html', {'courses_in_cart': courses_in_cart, 'courses_in_calendar': courses_in_calendar})
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

def addToSchedule(request, pk):
    if(request.user.is_authenticated):
        course = get_object_or_404(Course, pk = pk)
        course.course_added_to_schedule.add(request.user)
        course.save()
        return calendar(request)
    else:
        response = redirect('/accounts/login')
        return response

def removeFromSchedule(request, pk):
    if(request.user.is_authenticated):
        course = get_object_or_404(Course, pk = pk)
        course.course_added_to_schedule.remove(request.user)
        course.save()
        return calendar(request)
    else:
        response = redirect('/accounts/login')
        return response
    
def createSchedule(request, pk):
    if(request.method == 'POST'):

        #https://docs.djangoproject.com/en/4.2/topics/db/queries/
        #https://stackoverflow.com/questions/24963761/django-filtering-a-model-that-contains-a-field-that-stores-regex 

        if(Schedule.objects.filter(author = request.user).exists()):
            Schedule.objects.filter(author = request.user).delete() 

        current_schedule = Schedule.objects.create(author = request.user)

        #https://stackoverflow.com/questions/5481890/django-does-the-orm-support-the-sql-in-operator 
        courses_in_schedule_to_add = Course.objects.filter(course_added_to_schedule__in= [request.user.id])
        for curr_course in courses_in_schedule_to_add:
            current_schedule.courses.add(curr_course)
        current_schedule.save()    
        
        return calendar(request)


    else: 
        #Not trying to submit a course, should not go to this url
        response = redirect('/accounts/login')
        return response



def approveSchedule(request):
    #https://stackoverflow.com/questions/1746377/checking-for-content-in-django-request-post
    #https://docs.djangoproject.com/en/4.2/ref/request-response/
    if(request.user.is_authenticated and request.method == 'POST'): 
        if('approved' in request.POST):
            theSchedule = request.POST.get('scheduleID')
            mySchedule = get_object_or_404(Schedule, id=theSchedule)
            mySchedule.status = True 
            mySchedule.save()
        else:
            #The approve button was not pressed so therefor it must have been rejected
            theSchedule = request.POST.get('scheduleID')
            mySchedule = get_object_or_404(Schedule, id=theSchedule)
            mySchedule.isRejected = True
            mySchedule.save()

        schedules = Schedule.objects.all().filter(isRejected=False, status = False)
        template = loader.get_template('myapp/adminHome.html')
        return HttpResponse(template.render({'schedules':schedules}, request))

    else:
        response = redirect('/accounts/login')
        return response















def calendar(request):
    if(request.user.is_authenticated):  
        current_user = request.user
        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
        calendar_courses = []
        seen_classes = set()
        for i in range(len(courses_in_calendar)):
            course = courses_in_calendar[i]
            calendar_course = (CalendarObj(course))
            if calendar_course.course_id not in seen_classes:
                seen_classes.add(calendar_course.course_id)
                calendar_course.coursenum = i
            calendar_courses.append(calendar_course)
        mon,tue,wed,thu,fri=[],[],[],[],[]
        for course in calendar_courses:
            if "Mo" in course.course_days_of_week:
                if len(mon) != 0:
                    count = 0
                    for otherCourse in mon:
                        if (course.course_start_time != otherCourse.course_start_time and course.course_end_time != otherCourse.course_end_time 
                        and not(course.course_start_time > otherCourse.course_start_time and course.course_start_time < otherCourse.course_end_time) and  
                        not(course.course_end_time > otherCourse.course_start_time and course.course_end_time < otherCourse.course_end_time)):
                            count+= 1
                    if(count == len(mon)):
                        mon.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        course.course_added_to_cart.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    mon.append(course)
            if "Tu" in course.course_days_of_week:
                if len(tue) != 0:
                    count = 0
                    for otherCourse in tue:
                        if (course.course_start_time != otherCourse.course_start_time and course.course_end_time != otherCourse.course_end_time 
                        and not(course.course_start_time > otherCourse.course_start_time and course.course_start_time < otherCourse.course_end_time) and  
                        not(course.course_end_time > otherCourse.course_start_time and course.course_end_time < otherCourse.course_end_time)):
                            count+= 1
                    if(count == len(tue)):
                        tue.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        course.course_added_to_cart.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    tue.append(course)
            if "We" in course.course_days_of_week:
                if len(wed) != 0:
                    count = 0
                    for otherCourse in wed:
                        if (course.course_start_time != otherCourse.course_start_time and course.course_end_time != otherCourse.course_end_time 
                        and not(course.course_start_time > otherCourse.course_start_time and course.course_start_time < otherCourse.course_end_time) and  
                        not(course.course_end_time > otherCourse.course_start_time and course.course_end_time < otherCourse.course_end_time)):
                            count+= 1
                    if(count == len(wed)):
                        wed.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        course.course_added_to_cart.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    wed.append(course)
            if "Th" in course.course_days_of_week:
                if len(thu) != 0:
                    count = 0
                    for otherCourse in thu:
                        if (course.course_start_time != otherCourse.course_start_time and course.course_end_time != otherCourse.course_end_time 
                        and not(course.course_start_time > otherCourse.course_start_time and course.course_start_time < otherCourse.course_end_time) and  
                        not(course.course_end_time > otherCourse.course_start_time and course.course_end_time < otherCourse.course_end_time)):
                            count+= 1
                    if(count == len(thu)):
                        thu.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        course.course_added_to_cart.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    thu.append(course)
            if "Fr" in course.course_days_of_week:
                if len(fri) != 0:
                    count = 0
                    for otherCourse in fri:
                        if (course.course_start_time != otherCourse.course_start_time and course.course_end_time != otherCourse.course_end_time 
                        and not(course.course_start_time > otherCourse.course_start_time and course.course_start_time < otherCourse.course_end_time) and  
                        not(course.course_end_time > otherCourse.course_start_time and course.course_end_time < otherCourse.course_end_time)):
                            count+= 1
                    if(count == len(fri)):
                        fri.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        course.course_added_to_cart.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    fri.append(course)
        week = [mon, tue, wed, thu, fri]
        for i in range(len(week)):
            week[i] = sorted(week[i], key=lambda obj: obj.start_tag)
        week_dict = {"MON" : week[0], "TUE" : week[1], "WED" : week[2], "THU" : week[3], "FRI" : week[4]} 

        #Logic for passing the schedule object thorugh
        usersSchedule = None
        if(Schedule.objects.filter(author = request.user).exists()):
            usersSchedule = Schedule.objects.get(author = request.user)

        return render(request, 'myapp/calendar.html', {'week' : week_dict, 'schedule' : week, 'courses_in_calendar': courses_in_calendar, 'usersSchedule' : usersSchedule})
    else:
        response = redirect('/accounts/login')
        return response


"""
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

"""