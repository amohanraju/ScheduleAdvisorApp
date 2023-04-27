from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from myapp.models import Course, Schedule
from django.urls import reverse
from django.contrib import messages
import requests
from datetime import datetime
import re
import json

def download_classes():
    print("Starting!")
    url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1232'
    categories = requests.get(url).json()
    subs = categories.get("subjects")
    orgs = categories.get("acad_orgs")
    i = 0
    subjects = Course.objects.values_list('course_mnemonic', flat=True).distinct()
    for info in subs:
        subject = info['subject']
        print(subject+" "+str(i))
        i += 1
        if subject in subjects:
            continue
        class_url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.' \
        'IScript_ClassSearch?institution=UVA01&term=1232&subject=%s&page=1' % subject
        classes = requests.get(class_url).json()
        for course in classes:
            if len(course.get("meetings")) == 0:
                continue
            start = course.get("meetings")[0]['start_time']
            if (start != ""):
                start = datetime.strptime(course.get("meetings")[0]['start_time'], '%H.%M.%S.%f%z').strftime('%I:%M %p')
            end = course.get("meetings")[0]['end_time']
            if (end != ""):
                end = datetime.strptime(course.get("meetings")[0]['end_time'], '%H.%M.%S.%f%z').strftime('%I:%M %p')
            course_model_instance = Course(
                course_id=course.get('crse_id'),
                course_section=course.get('class_section'),
                course_catalog_nbr=course.get('catalog_nbr'),

                course_subject=course.get('descr'),
                course_mnemonic=course.get('subject'),
                course_credits=course.get('units'),
                course_type=course.get('section_type'),

                course_instructor=course.get("instructors")[0]['name'],
                course_location=course.get("meetings")[0]['facility_descr'],

                course_size=course.get('class_capacity'),
                course_enrollment_total=course.get('enrollment_total'),
                course_waitlist_total=course.get('wait_tot'),
                course_waitlist_cap=course.get('wait_cap'),

                course_days_of_week=course.get("meetings")[0]['days'],
                course_start_time=start,
                course_end_time=end,

            )
            course_model_instance.course_enrollment_availability = course.get('enrollment_available')
            if (course_model_instance not in Course.objects.all()):
                course_model_instance.save()
                course_model_instance.course_added_to_cart.set([])
                course_model_instance.save()
    print()
    url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearchOptions?institution=UVA01&term=1232'
    categories = requests.get(url).json()
    respons = categories.get("subjects")
    i = 0
    for info in respons:
        subject = info['subject']
        print(subject+" "+str(i))
        i += 1
class IndexView(generic.ListView):
    template_name='myapp/index.html'
    def get_queryset(self):
        return

def courseforum_view(request):
    return redirect('https://thecourseforum.com/')

def profile(request):
    if request.user.is_authenticated:
        usersSchedule = None
        if(Schedule.objects.filter(author = request.user).exists()):
            usersSchedule = Schedule.objects.get(author = request.user)
        if request.user.is_superuser:
            schedules = Schedule.objects.all().filter(isRejected=False, status = False)
            template = loader.get_template('myapp/adminHome.html')
            return HttpResponse(template.render({'schedules':schedules, 'usersSchedule':usersSchedule}, request))
        
        template = loader.get_template('myapp/profile.html')
        return HttpResponse(template.render({}, request))
    else:
        response = redirect('/accounts/login')
        return response
    
class CourseView(generic.ListView):
    template_name='myapp/courses.html'
    def get_queryset(self):
        return

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
        self.conflict = False
        self.start_tag, self.end_tag = self.populate_tags()
        self.short_class = self.populate_time()
        self.in_calendar = False
    
    def populate_tags(self):
        start_tag = str(self.course_start_time)[0:2] + "_" + str(self.course_start_time)[3:5]
        end_tag = str(self.course_end_time)[0:2] + "_" + str(self.course_end_time)[3:5]
        if start_tag[0] == '0':
            start_tag = start_tag[1:]
        if end_tag[0] == '0':
            end_tag = end_tag[1:]
        
        return start_tag, end_tag
    
    def populate_time(self):
        start = datetime.strptime(self.course_start_time, "%I:%M %p")
        end = datetime.strptime(self.course_end_time, "%I:%M %p")
        diff = end-start
        mins = int(diff.total_seconds()/ 60)
        # print(self.course_subject)
        # print(mins)
        if mins <= 50:
            return True
        else:
            return False

# def api_data(request):
#     class_dept = request.GET.get("classes")
#     print(class_dept)
#     query = request.GET.get("query")
#     if query:
#         department = query.split()[0].upper()
#         number = query.split()[1]
#         url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.' \
#             'IScript_ClassSearch?institution=UVA01&term=1232&subject=%s&catalog_nbr=%s&page=1' % (department, query.split()[1])
#         classes = requests.get(url).json()
#         if len(query.split()) == 2:
#             subject, catalog_nbr = query.split()
#             # print(catalog_nbr)
#             temp = []
#             # print(len(classes))
#             for c in classes:
#                 if c.get('catalog_nbr') == catalog_nbr:
#                     temp.append(c)
#             classes = temp
#             print(type(classes))
        
#     else:
#         url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.' \
#             'IScript_ClassSearch?institution=UVA01&term=1232&subject=%s&page=1' % class_dept
#         print(url)
#         classes = requests.get(url).json()
    
#     #if len(query.split()) == 2:
#            # subject, catalog_nbr = query.split()
#     #print(classes)
#     if request.method == 'GET':
#         #return HttpResponse(url)
#         #courses_in_calendar = Course.objects.filter(course_added_to_schedule = request.user)
#         class_objects = []
#         if(len(classes) > 0):
#             for course in classes:
#                 if(not Course.objects.filter(course_id= course.get("crse_id"), course_section= course.get("class_section"), course_catalog_nbr=course.get("catalog_nbr"), course_instructor = course.get("instructors")[0]['name']).exists()):
#                     start = course.get("meetings")[0]['start_time']
#                     if (start != ""):
#                         start = datetime.strptime(course.get("meetings")[0]['start_time'], '%H.%M.%S.%f%z').strftime('%I:%M %p')
#                     end = course.get("meetings")[0]['end_time']
#                     if (end != ""):
#                         end = datetime.strptime(course.get("meetings")[0]['end_time'], '%H.%M.%S.%f%z').strftime('%I:%M %p')
#                     course_model_instance = Course(
#                         course_id = course.get('crse_id'),
#                         course_section = course.get('class_section'),
#                         course_catalog_nbr = course.get('catalog_nbr'),

#                         course_subject = course.get('descr'),
#                         course_mnemonic = course.get('subject'),

#                         course_instructor = course.get("instructors")[0]['name'],
#                         course_location = course.get("meetings")[0]['facility_descr'],

#                         course_size = course.get('class_capacity'),
#                         course_enrollment_total = course.get('enrollment_total'),
#                         course_waitlist_total = course.get('wait_tot'),
#                         course_waitlist_cap = course.get('wait_cap'),

#                         course_days_of_week = course.get("meetings")[0]['days'],
#                         course_start_time = start,
#                         course_end_time = end,

#                     )
#                     course_model_instance.course_enrollment_availability = course.get('enrollment_available')
#                     course_model_instance.save()
#                     course_model_instance.course_added_to_cart.set([])
#                     course_model_instance.save()
#         #primary_keys = [instance.pk for instance in class_objects]
#         # filtered_classes = [c for c in classes if query.lower() in c.get("descr").lower()]
#         # print(filtered_classes)
#         classes_json = json.dumps(classes)
#         finalList = zip(class_objects, classes)
#         tuples = []
#         for i in range(len(class_objects)):
#             tuples.append((class_objects[i], classes[i]))
#         for course in class_objects:
#             course.course_enrollment_availability = course.course_enrollment_availability[0]
#         context = {'content': finalList, 'classes_json': classes_json, 'classes' : tuples,}
#         return render(request, 'myapp/courses.html', context)
#         #return render(request, 'myapp/courses.html', {'classes' : classes, 'primary_keys' : primary_keys})
#     else:
#         classes_json = json.dumps(classes)
#         context = {'classes_json': classes_json}
#         print(classes_json)
#         return render(request, 'myapp/courses.html', context)

def api_data(request):
    class_dept = request.GET.get("classes")
    query = request.GET.get("query")
    courses = []
    if query:
        mnemonics = Course.objects.values_list('course_mnemonic',flat=True).distinct()
        #Search by mnemonic and course number
        if query.split()[0].upper() in mnemonics:
            mnemonic = query.split()[0].upper()
            number = query.split()[1]
            courses = Course.objects.filter(course_mnemonic=mnemonic, course_catalog_nbr=number)
        #Search by description
        else:
            courses = Course.objects.filter(course_subject = query)
    else:
        url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.' \
            'IScript_ClassSearch?institution=UVA01&term=1232&subject=%s&page=1' % class_dept
        classes = requests.get(url).json()
    if request.method == 'GET':
        for course in courses:
            course.course_enrollment_availability = re.sub("[^0-9]", "", course.course_enrollment_availability)
        context = {'classes': courses}
        return render(request, 'myapp/courses.html', context)
    else:
        classes_json = json.dumps(classes)
        context = {'classes_json': classes_json}
        print(classes_json)
        return render(request, 'myapp/courses.html', context)
    

def shoppingCart(request):
    if(request.user.is_authenticated):  
        current_user = request.user
        all_courses = Course.objects.all()
        courses_in_cart = []
        courses_in_cart = Course.objects.filter(course_added_to_cart = current_user)
        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
        courseVar = 'course'
        for cart_course in courses_in_cart:
            cart_course.course_enrollment_availability = re.sub("[^0-9]", "", cart_course.course_enrollment_availability)
            for cal_course in courses_in_calendar:
                if (cart_course not in courses_in_calendar):
                    cart_course.in_calendar = False
                    if dtime_conflict(cart_course, cal_course) and (cart_course != cal_course):
                        cart_course.conflict = True
                        print(cart_course.course_subject+" conflicts with "+cal_course.course_subject)
                else:
                    cart_course.in_calendar = True
        return render(request, 'myapp/shoppingCart.html', {'courses_in_cart': courses_in_cart, 'courses_in_calendar': courses_in_calendar, 'courseVar': courseVar})
    else:
        response = redirect('/accounts/login')
        return response

def addToCart(request, pk):
    if(request.user.is_authenticated):  
        #https://www.youtube.com/watch?v=PXqRPqDjDgc
        course = get_object_or_404(Course, pk = pk)
        course.course_added_to_cart.add(request.user)
        course.save()
        messages.success(request,"Successfully added "+course.course_mnemonic+" "+course.course_catalog_nbr+" to your cart!")
        return shoppingCart(request)
    else:
        response = redirect('/accounts/login')
        return response

def removeFromCart(request, pk):
    #Get user from route and then remove the associated course and save
    course = get_object_or_404(Course, pk = pk)
    course.course_added_to_cart.remove(request.user)
    course.save()
    messages.success(request,"Successfully removed "+course.course_mnemonic+" "+course.course_catalog_nbr+" from your cart!")
    return shoppingCart(request)

def addToSchedule(request, pk):
    if(request.user.is_authenticated):
        course = get_object_or_404(Course, pk = pk)
        courses_in_calendar = Course.objects.filter(course_added_to_schedule = request.user)
        conflict = False
        conflict_course = course
        for cal_course in courses_in_calendar:
            if dtime_conflict(course, cal_course):
                conflict = True
                conflict_course = cal_course
                break
        if not conflict:
            messages.success(request,"Successfully added "+course.course_mnemonic+" "+course.course_catalog_nbr+" to your schedule!")
            course.course_added_to_schedule.add(request.user)
            course.save()
            return calendar(request)
        else:
            messages.error(request, "Could not add "+course.course_mnemonic+" "+course.course_catalog_nbr+" due to time conflict with "+
                           conflict_course.course_mnemonic+" "+conflict_course.course_catalog_nbr+".")
            #return HttpResponseRedirect('accounts/profile/shopping_cart')
            #return render(request, 'myapp/shoppingCart.html')
            #return redirect('.')
            #return HttpResponseRedirect(request.path_info)
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        response = redirect('/accounts/login')
        return response

def removeFromSchedule(request, pk):
    if(request.user.is_authenticated):
        course = get_object_or_404(Course, pk = pk)
        course.course_added_to_schedule.remove(request.user)
        course.save()
        messages.success(request,"Successfully removed "+course.course_mnemonic+" "+course.course_catalog_nbr+" from your schedule!")
        return shoppingCart(request)
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
                        if (not time_conflict(course, otherCourse)):
                            count+= 1
                    if(count == len(mon)):
                        mon.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    mon.append(course)
            if "Tu" in course.course_days_of_week:
                if len(tue) != 0:
                    count = 0
                    for otherCourse in tue:
                        if (not time_conflict(course, otherCourse)):
                            count+= 1
                    if(count == len(tue)):
                        tue.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    tue.append(course)
            if "We" in course.course_days_of_week:
                if len(wed) != 0:
                    count = 0
                    for otherCourse in wed:
                        if (not time_conflict(course, otherCourse)):
                            count+= 1
                    if(count == len(wed)):
                        wed.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    wed.append(course)
            if "Th" in course.course_days_of_week:
                if len(thu) != 0:
                    count = 0
                    for otherCourse in thu:
                        if (not time_conflict(course, otherCourse)):
                            count+= 1
                    if(count == len(thu)):
                        thu.append(course)
                    else:
                        course.course_added_to_schedule.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    thu.append(course)
            if "Fr" in course.course_days_of_week:
                if len(fri) != 0:
                    count = 0
                    for otherCourse in fri:
                        if (not time_conflict(course, otherCourse)):
                            count+= 1
                    if(count == len(fri)):
                        fri.append(course)
                    else:
                        # message = "Could not add "+course.course_mnemonic+" "+course.course_catalog_nbr+" due to time conflict with "+otherCourse.course_mnemonic+" "+otherCourse.course_catalog_nbr+"."
                        # if message not in error_messages:
                        #     error_messages.add(message)
                        course.course_added_to_schedule.remove(request.user)
                        #course.course_added_to_cart.remove(request.user)
                        courses_in_calendar = Course.objects.filter(course_added_to_schedule = current_user)
                else:
                    fri.append(course)
        week = [mon, tue, wed, thu, fri]
        for i in range(len(week)):
            week[i] = sorted(week[i], key=lambda obj: obj.start_tag)
        week_dict = {"Monday" : week[0], "Tuesday" : week[1], "Wednesday" : week[2], "Thursday" : week[3], "Friday" : week[4]} 
        #Logic for passing the schedule object thorugh
        usersSchedule = None
        if(Schedule.objects.filter(author = request.user).exists()):
            usersSchedule = Schedule.objects.get(author = request.user)
        courseVar = 'course'
        return render(request, 'myapp/calendar.html', {'week' : week_dict, 'schedule' : week, 'courses_in_calendar': courses_in_calendar, 'usersSchedule' : usersSchedule, 'courseVar': courseVar})

    else:
        response = redirect('/accounts/login')
        return response

def time_conflict(course1, course2):
        # if (course1.course_start_time != course2.course_start_time and course1.course_end_time != course2.course_end_time 
        #     and not(course1.course_start_time > course2.course_start_time and course1.course_start_time < course2.course_end_time) and  
        #     not(course1.course_end_time > course2.course_start_time and course1.course_end_time < course2.course_end_time)):
        #     return False
        # else:
        #     return True
        if (course1.course_start_time == '' or course1.course_end_time == '' or course2.course_start_time == '' or course2.course_end_time == ''):
            return False
        c1_start = datetime.strptime(course1.course_start_time, "%I:%M %p")
        c1_end = datetime.strptime(course1.course_end_time, "%I:%M %p")
        c2_start = datetime.strptime(course2.course_start_time, "%I:%M %p")
        c2_end = datetime.strptime(course2.course_end_time, "%I:%M %p")
        if (c1_start == c2_start):
            return True
        if (c1_end == c2_end):
            return True
        if (c1_start <= c2_end and c2_start <= c1_end):
            return True
        return False

def dtime_conflict(course1, course2):
    week = ["Mo", "Tu", "We", "Th", "Fr"]
    for day in week:
        if day in course1.course_days_of_week and day in course2.course_days_of_week and time_conflict(course1, course2):
            return True
    return False

    # if "Mo" in course1.course_days_of_week and "Mo" in course2.course_days_of_week:
    #     if time_conflict(course1, course2):
    #         return True
    # if "Tu" in course1.course_days_of_week and "Tu" in course2.course_days_of_week:
    #     if time_conflict(course1, course2):
    #         return True
    # if "We" in course1.course_days_of_week and "We" in course2.course_days_of_week:
    #     if time_conflict(course1, course2):
    #         return True
    # if "Th" in course1.course_days_of_week and "Th" in course2.course_days_of_week:
    #     if time_conflict(course1, course2):
    #         return True
    # if "Fr" in course1.course_days_of_week and "Fr" in course2.course_days_of_week:
    #     if time_conflict(course1, course2):
    #         return True
    # return False