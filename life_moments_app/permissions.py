from rest_framework import permissions
from life_moments_app.models import *
import redis
from django.conf import settings
session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
     
class IsAuth(permissions.BasePermission): 
    def has_permission(self, request, view): 
        access_token = request.COOKIES.get("session_id", None)
 
        if access_token is None: 
            return False 
 
        try: 
            session_storage.get(access_token).decode('utf-8') 
        except Exception as e: 
            return False 
 
        return True