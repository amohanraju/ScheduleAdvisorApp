from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('accounts/profile/', views.profile, name='profile'),
    path('accounts/profile/browse_courses', views.api_data, name='api_data'),
    path('accounts/profile/shopping_cart', views.shoppingCart, name="shoppingCart"),
    path('accounts/addToCart/<int:pk>/', views.addToCart, name = 'addToCart'),
    path('accounts/removeFromCart/<int:pk>/', views.removeFromCart, name = 'removeFromCart')
]