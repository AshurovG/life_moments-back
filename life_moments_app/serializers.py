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
        fields = ['id', 'username', 'profile_picture', 'rating']

class MomentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moments
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = "__all__"

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Likes
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['id', 'text', 'publication_date', 'id_author', 'id_moment', 'likes', 'author']

    def get_likes(self, obj):
        return [like.id_author.id for like in obj.comment_like.all()]

    def get_author(self, obj):
        # Получаем объект CustomUser по id_author и сериализуем его
        author = CustomUser.objects.get(id=obj.id_author.id)
        return SubscriptionUserSerializer(author).data

