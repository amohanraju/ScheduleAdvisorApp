from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/browse_courses', views.api_data, name='api_data'),
]