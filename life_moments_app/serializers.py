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
    # likes_count = serializers.IntegerField()
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['text', 'publication_date', 'id_author', 'id_moment', 'likes']

    def get_likes(self, obj):
        # Возвращаем список идентификаторов лайков для комментария
        return [like.id_author.id for like in obj.comment_like.all()]
