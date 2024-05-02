from django.shortcuts import render
from datetime import date
from life_moments_app.models import *
from life_moments_app.serializers import *
# from life_moments_app.permissions import *
from life_moments_app.permissions import IsAuth
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework import status
from django.contrib.auth import authenticate, login
from django.http import HttpResponseServerError
import uuid
from django.conf import settings
import redis
from minio import Minio

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
        if self.model_class.objects.filter(email=request.data['email']).exists():
            return Response({'status': 'Exist'}, status=400)
        
        if 'profile_picture' in request.FILES:
            file = request.FILES['profile_picture']
            
            client = Minio(endpoint="localhost:9000",
                        access_key='minioadmin',
                        secret_key='minioadmin',
                        secure=False)

            bucket_name = 'life-moments'
            file_name = file.name
            file_path = "http://localhost:9000/life-moments/" + file_name
            print(file_path)
        
        try:
            client.put_object(bucket_name, file_name, file, length=file.size, content_type=file.content_type)
            print("Файл успешно загружен в Minio.")
            request.data['profile_picture'] = file_path
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():

                currentDate = datetime.now().strftime('%Y-%m-%d')
                self.model_class.objects.create_user(
                    username=serializer.data['username'],
                    email=serializer.data['email'],
                    password=serializer.data['password'],
                    profile_picture=file_path,
                    rating=0, # TODO: Сделать функцию расчета рейтинга
                    registration_date=currentDate,
                )
                
                random_key = str(uuid.uuid4())
                session_storage.set(random_key, serializer.data['email'])

                user_data = {
                    "username": request.data['username'],
                    "email": request.data['email'],
                    "profile_picture": file_path,
                    "rating": 0, # TODO: Сделать функцию расчета рейтинга
                    "registration_date": currentDate
                }
                
                response = Response(user_data, status=status.HTTP_201_CREATED)
                response.set_cookie("session_id", random_key)
                return response
        except Exception as e:
            print("Ошибка при загрузке файла в Minio:", str(e))
            return HttpResponseServerError('An error occurred during file upload.')

        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, username)
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
                username = session_storage.get(ssid).decode('utf-8')
                user = CustomUser.objects.get(username=username)
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
                return Response({'status': 'Error', 'message': 'Session does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'status': 'Error', 'message': 'Cookies were not transmitted'}, status=status.HTTP_400_BAD_REQUEST)
