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

class MinioClientSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MinioClientSingleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.client = Minio(endpoint="localhost:9000",
                             access_key='minioadmin',
                             secret_key='minioadmin',
                             secure=False)
        self.bucket_name = 'life-moments'

def generate_unique_file_name(original_file_name):
    file_extension = original_file_name.split('.')[-1]
    unique_file_name = f"{uuid.uuid4()}.{file_extension}"
    return unique_file_name

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request):
        if self.model_class.objects.filter(email=request.data['email']).exists() or self.model_class.objects.filter(username=request.data['username']).exists():
            return Response({'status': 'Exist'}, status=400)
        print(request.FILES)
        if 'profile_picture' in request.FILES:
            file = request.FILES['profile_picture']
            
            client = Minio(endpoint="localhost:9000",
                        access_key='minioadmin',
                        secret_key='minioadmin',
                        secure=False)

            bucket_name = 'life-moments'
            file_name = generate_unique_file_name(file.name)
            # file_name = file.name
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
                session_storage.set(random_key, serializer.data['username'])

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
        print(username, password)
        
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
                print("username isssss ", username)
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
    
    def update(self, request):
        try:
            ssid = request.COOKIES["session_id"]
            if session_storage.exists(ssid):
                old_username = session_storage.get(ssid).decode('utf-8')
                print(old_username)
                user = CustomUser.objects.get(username=old_username)

            email = request.data.get('email')
            username = request.data.get('username')
            if (email):
                if self.model_class.objects.filter(email=email).exclude(id=user.id).exists():
                    return Response({'status': 'email exists'}, status=status.HTTP_400_BAD_REQUEST)
            if (username):
                if self.model_class.objects.filter(username=username).exclude(id=user.id).exists():
                    return Response({'status': 'username exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            if 'profile_picture' in request.FILES:
                minio_client = MinioClientSingleton()
                client = minio_client.client
                bucket_name = minio_client.bucket_name
                old_file_path = user.profile_picture
                if old_file_path and 'profile_picture' in request.FILES:
                    old_file_name = old_file_path.split('/')[-1]
                    client.remove_object(bucket_name, old_file_name)
                    print("Файл успешно удален из Minio.")

                if 'profile_picture' in request.FILES:
                    file = request.FILES['profile_picture']
                    file_name = generate_unique_file_name(file.name)
                    file_path = "http://localhost:9000/life-moments/" + file_name
                
                try:
                    client.put_object(bucket_name, file_name, file, length=file.size, content_type=file.content_type)
                    print("Файл успешно загружен в Minio.")
                    request.data['profile_picture'] = file_path
                except Exception as e:
                    print("Ошибка при загрузке файла в Minio:", str(e))
                    return HttpResponseServerError('An error occurred during file upload.')
                
            serializer = self.serializer_class(user, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save() # Обновление пользователя в базе данных
                if (username):
                    if 'username' in request.data and request.data['username'] != old_username:
                        new_username = request.data['username']
                        # Удаление старой сессии
                        session_storage.delete(ssid)
                        # Создание новой сессии с новым ключом, но с тем же значением
                        session_storage.set(ssid, new_username)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
                return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 'Error', 'session was not found': str(e)}, status=status.HTTP_403_FORBIDDEN)
        
class MomentViewSet(viewsets.ModelViewSet):
    queryset = Moments.objects.all()
    serializer_class = MomentSerializer
    model_class = Moments
    authentication_classes = []
    permission_classes = [IsAuth]

    def create(self, request):
        try:
            ssid = request.COOKIES["session_id"]
            print(request.data)
            if session_storage.exists(ssid):
                username = session_storage.get(ssid).decode('utf-8')
                user = CustomUser.objects.get(username=username)
                if 'image' in request.FILES:
                    file = request.FILES['image']
                    minio_client = MinioClientSingleton()
                    client = minio_client.client
                    bucket_name = minio_client.bucket_name
                    file_name = generate_unique_file_name(file.name)
                    file_path = "http://localhost:9000/life-moments/" + file_name
                    print(file_path)
                    try:
                        client.put_object(bucket_name, file_name, file, length=file.size, content_type=file.content_type)
                    except Exception as e:
                        return HttpResponseServerError('An error occurred during file upload.')
                    
                currentDate = datetime.now().strftime('%Y-%m-%d')
                moment_data = {
                    'title': request.data.get('title'),
                    'image': file_path,
                    'publication_date': currentDate,
                    'id_author': user.id,
                }

                if request.data.get('description') is not None:
                    moment_data['description'] = request.data.get('description')

                serializer = MomentSerializer(data=moment_data, partial=True)

                if serializer.is_valid():
                    moment = serializer.save()
                    return Response({'status': 'success', 'moment_id': moment.id}, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': 'success'}, status=status.HTTP_200_OK)

        except:
            return Response({'status': 'Error'}, status=status.HTTP_400_BAD_REQUEST)