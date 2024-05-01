from django.contrib import admin
from django.urls import path, include
from life_moments_app import views

urlpatterns = [
    path('books', views.GetBooks, name='getBooks'),
    path('login',  views.login_view, name='auth'),
    path('logout', views.logout_view, name='logout'),
    path('user_info', views.user_info, name='user_info')
]
