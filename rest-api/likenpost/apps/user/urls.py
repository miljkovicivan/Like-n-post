from django.conf.urls import url, include
from django.urls import path
from rest_framework import routers
from likenpost.apps.user.views import UserView

router = routers.DefaultRouter()
app_name = 'user'

urlpatterns = [
    path('<int:pk>/', UserView.as_view(), name='user'),
]
