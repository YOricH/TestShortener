# project URL Configuration

from django.urls import path, include


urlpatterns = [path('', include('project.shortener.urls'))]
