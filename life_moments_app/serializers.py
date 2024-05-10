from life_moments_app.models import *
from rest_framework import serializers
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(required=False)
    registration_date = serializers.DateField(required=False)
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'description', 'profile_picture', 'rating', 'registration_date']

class SubscriptionUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['username', 'profile_picture', 'rating']

class MomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moments
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = "__all__"