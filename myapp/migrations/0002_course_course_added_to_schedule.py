# Generated by Django 4.1.7 on 2023-04-01 22:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='course_added_to_schedule',
            field=models.ManyToManyField(related_name='courses_in_schedule', to=settings.AUTH_USER_MODEL),
        ),
    ]