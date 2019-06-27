# project/shortener/urls.py
# 'Shortener' app URL Configuration.

from shortener.api.viewsets import DirectionViewSet, UserDirectionViewSet
from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'directions', DirectionViewSet)
router.register(r'userdirections', UserDirectionViewSet)


urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('<str:subpart>', views.redirect),
]
