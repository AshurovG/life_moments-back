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
    path('user/subscribe', views.UserViewSet.as_view({'post': 'subscribe'}), name='user_subscribe'),
    path('user/unsubscribe', views.UserViewSet.as_view({'delete': 'unsubscribe'}), name='user_unsubscribe'),
    path('user/actions', views.UserViewSet.as_view({'get': 'getLastActions'}), name='user_actions'),
    path('user/search', views.UserViewSet.as_view({'get': 'searchUsers'}), name='user_search'),
    
    path('moments', views.MomentViewSet.as_view({'get': 'getMoments'}), name='moment_get'),
    path('moments/create', views.MomentViewSet.as_view({'post': 'create'}), name='moment_create'),
    path('moments/detailed', views.MomentViewSet.as_view({'get': 'getMoment'}), name='moment_detailed'),
    path('moments/like', views.MomentViewSet.as_view({'post': 'makeLike'}), name='moment_like'),
    path('moments/remove_like', views.MomentViewSet.as_view({'delete': 'removeLike'}), name='moment_remove_like'),
    path('moments/comment', views.MomentViewSet.as_view({'post': 'leaveComment'}), name='moment_leave_comment'),
    path('moments/comment/likes', views.MomentViewSet.as_view({'get': 'getCommentLikes'}), name='comment_likes'),
    path('moments/likes', views.MomentViewSet.as_view({'get': 'getMomentLikes'}), name='moment_likes'),
    path('moments/search', views.MomentViewSet.as_view({'get': 'searchMoments'}), name='moment_search'),
    path('moments/random', views.MomentViewSet.as_view({'get': 'getRandomMoments'}), name='moment_random'),

]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
]