# Generated by Django 4.1.7 on 2023-03-19 21:33

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.CharField(max_length=255)),
                ('course_section', models.CharField(max_length=255)),
                ('course_catalog_nbr', models.CharField(max_length=255)),
                ('course_subject', models.CharField(max_length=255)),
                ('course_mnemonic', models.CharField(max_length=255)),
                ('course_description', models.CharField(max_length=1000)),
                ('course_instructor', models.CharField(max_length=255)),
                ('course_location', models.CharField(max_length=255)),
                ('course_size', models.CharField(max_length=255)),
                ('course_enrollment_total', models.CharField(max_length=255)),
                ('course_enrollment_availability', models.CharField(max_length=255)),
                ('course_waitlist_total', models.CharField(max_length=255)),
                ('course_waitlist_cap', models.CharField(max_length=255)),
                ('course_added_to_cart', models.ManyToManyField(related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
