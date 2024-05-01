from life_moments_app.models import *
from rest_framework import serializers
from datetime import datetime


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(required=False)
    registration_date = serializers.DateField(required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'profile_picture', 'rating', 'registration_date']