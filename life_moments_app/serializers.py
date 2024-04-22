from life_moments_app.models import *
from rest_framework import serializers
from datetime import datetime


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = "__all__"