from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from life_moments_app import views

router = routers.DefaultRouter()

router.register(r'user', views.UserViewSet, basename='user')

urlpatterns = [
    path('books', views.GetBooks, name='getBooks'),

    path('user/register', views.UserViewSet.as_view({'post': 'create'}), name='user_register'),
    # path('login',  views.login_view, name='auth'),
    # path('logout', views.logout_view, name='logout'),
    # path('user_info', views.user_info, name='user_info')
]
