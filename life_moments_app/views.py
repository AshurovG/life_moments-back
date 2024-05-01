from django.shortcuts import render
from datetime import date
from life_moments_app.models import *
from life_moments_app.serializers import *
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
import uuid
from django.conf import settings
import redis

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

@api_view(['GET'])
def GetBooks(request):
    books = Books.objects
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request):
        print('req is', request.data)
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            currentDate = datetime.now().strftime('%Y-%m-%d')
            self.model_class.objects.create_user(
                username=serializer.data['username'],
                email=serializer.data['email'],
                password=serializer.data['password'],
                profile_picture=serializer.data['profile_picture'],
                rating=0, # TODO: Сделать функцию расчета рейтинга
                registration_date=currentDate,
            )
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, serializer.data['email'])
            user_data = {
                "username": request.data['username'],
                "email": request.data['email'],
                "profile_picture": request.data['profile_picture'],
                "rating": 0, # TODO: Сделать функцию расчета рейтинга
                "registration_date": currentDate
            }

            print('user data is ', user_data)
            response = Response(user_data, status=status.HTTP_201_CREATED)
            response.set_cookie("session_id", random_key)
            return response
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, email)
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "profile_picture": user.profile_picture,
                "rating": user.rating,
                "registration_date": user.registration_date,
            }
            response = Response(user_data, status=status.HTTP_201_CREATED)
            response.set_cookie("session_id", random_key, samesite="Lax", max_age=30 * 24 * 60 * 60)
            return response
        else:
            return Response({"error": "login failed"}, status=status.HTTP_400_BAD_REQUEST)
        
    # @permission_classes([IsAuth])
    def logout(self, request):
        ssid = request.COOKIES["session_id"]
        if session_storage.exists(ssid):
            session_storage.delete(ssid)
            response_data = {'status': 'Success'}
        else:
            response_data = {'status': 'Error', 'message': 'Session does not exist'}
        return Response(response_data)
        
    def info(self, request):
        try:
            ssid = request.COOKIES["session_id"]
            if session_storage.exists(ssid):
                email = session_storage.get(ssid).decode('utf-8')
                user = CustomUser.objects.get(email=email)
                user_data = {
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "profile_picture": user.profile_picture,
                    "rating": user.rating,
                    "registration_date": user.registration_date
                }
                return Response(user_data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'Error', 'message': 'Session does not exist'})
        except:
            return Response({'status': 'Error', 'message': 'Cookies are not transmitted'})
