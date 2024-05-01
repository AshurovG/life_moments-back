from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from life_moments_app import views

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet, basename='user')

api_urlpatterns = [
    path('books', views.GetBooks, name='getBooks'),
    path('user/register', views.UserViewSet.as_view({'post': 'create'}), name='user_register'),
    path('user/login', views.UserViewSet.as_view({'post': 'login'}), name='user_login'),
    path('user/info', views.UserViewSet.as_view({'get': 'info'}), name='user_info'),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]