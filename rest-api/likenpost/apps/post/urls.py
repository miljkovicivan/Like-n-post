from django.urls import path
from rest_framework import routers
from likenpost.apps.post.views import PostViewSet

router = routers.DefaultRouter()

app_name = 'post'

urlpatterns = [
        path('', PostViewSet, name='post')
    ]
