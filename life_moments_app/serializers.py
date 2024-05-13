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
        fields = ['id', 'username', 'profile_picture', 'rating', 'description']

# class MomentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Moments
#         fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = "__all__"

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
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
    
# class MomentSerializer(serializers.ModelSerializer):
#     likes = serializers.SerializerMethodField()

#     class Meta:
#         model = Moments
#         fields = ['id', 'title', 'image', 'description', 'publication_date', 'id_author', 'likes']


#     def get_likes(self, obj):
#         print('dfd')
#         return [like.id_author.id for like in obj.moment_like.all()]

class MomentSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Moments
        fields = ['id', 'title', 'image', 'description', 'publication_date', 'id_author', 'likes', 'tags', 'comments']

    def get_tags(self, obj):
        # Возвращает список идентификаторов тегов, связанных с моментом
        return [tag.title for tag in obj.moment_tag.all()]

    def get_comments(self, obj):
        # Возвращает список сериализованных комментариев, связанных с моментом
        comments = obj.moment_comment.all()
        return CommentSerializer(comments, many=True).data

    def get_likes(self, obj):
        # Возвращает список идентификаторов авторов лайков, связанных с моментом
        return [like.id_author.id for like in obj.moment_like.all()]


# class MomentSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True, read_only=True)
#     likes = LikeSerializer(many=True, read_only=True)
#     comments = CommentSerializer(many=True, read_only=True)

#     class Meta:
#         model = Moments
#         fields = ['id', 'title', 'image', 'description', 'publication_date', 'id_author', 'tags', 'likes', 'comments']