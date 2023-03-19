from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Course(models.Model):
    course_id = models.CharField(max_length=255)
    course_section = models.CharField(max_length=255)
    course_catalog_nbr = models.CharField(max_length=255)

    course_subject = models.CharField(max_length=255)
    course_mnemonic = models.CharField(max_length=255)

    course_instructor = models.CharField(max_length=255)
    course_location = models.CharField(max_length=255)

    course_size = models.CharField(max_length=255)
    course_enrollment_total = models.CharField(max_length=255)
    course_enrollment_availability = models.CharField(max_length=255)
    course_waitlist_total = models.CharField(max_length=255)
    course_waitlist_cap = models.CharField(max_length=255)

    course_days_of_week = models.CharField(max_length=255)
    course_start_time = models.CharField(max_length=255)
    course_end_time = models.CharField(max_length=255)

    course_added_to_cart = models.ManyToManyField(User, related_name="courses")
    
