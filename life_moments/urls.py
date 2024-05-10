from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from life_moments_app import views

router = routers.DefaultRouter()
router.register(r'user', views.AuthViewSet, basename='user')

api_urlpatterns = [
    path('user/register', views.AuthViewSet.as_view({'post': 'create'}), name='user_register'),
    path('user/login', views.AuthViewSet.as_view({'post': 'login'}), name='user_login'),
    path('user/logout', views.AuthViewSet.as_view({'post': 'logout'}), name='user_logout'),
    path('user/info', views.AuthViewSet.as_view({'get': 'info'}), name='user_info'),
    path('user/update', views.AuthViewSet.as_view({'put': 'update'}), name='user_update'),

    path('user/detailed', views.AuthViewSet.as_view({'get': 'detailed'}), name='user_detailed'),
    path('user/subscribers', views.UserViewSet.as_view({'get': 'getSubscribers'}, name='user_subscribers')),
    path('user/subscriptions', views.UserViewSet.as_view({'get': 'getSubscriptions'}, name='user_subscriptions')),

    path('moments/create', views.MomentViewSet.as_view({'post': 'create'}), name='moment_create'),
    path('moments/detailed', views.MomentViewSet.as_view({'get': 'getMoment'}), name='moment_detailed'),
    path('moments/like', views.MomentViewSet.as_view({'post': 'makeLike'}), name='moment_like'),
    path('moments/remove_like', views.MomentViewSet.as_view({'delete': 'removeLike'}), name='moment_remove_like')
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]