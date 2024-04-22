from django.contrib import admin
from django.urls import path, include
from life_moments_app import views

urlpatterns = [
    path('books', views.GetBooks, name='getBooks'),
]
