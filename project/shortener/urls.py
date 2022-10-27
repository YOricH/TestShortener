# project/shortener/urls.py
# 'Shortener' app URL Configuration.

from .api.viewsets import DirectionViewSet, UserDirectionViewSet
from django.urls import path, include
from rest_framework import routers
from .views import index, redirect


router = routers.DefaultRouter()
router.register(r'directions', DirectionViewSet)
router.register(r'userdirections', UserDirectionViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('<str:subpart>', redirect),
    path('', index, name='index'),
]
