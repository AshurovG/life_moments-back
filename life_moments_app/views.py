from django.shortcuts import render
from datetime import date
from life_moments_app.models import *
from life_moments_app.serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse

@api_view(['GET'])
def GetBooks(request):
    books = Books.objects
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)