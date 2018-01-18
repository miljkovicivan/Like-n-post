from rest_framework import viewsets, generics, permissions
from django.contrib.auth.models import User
from likenpost.apps.user.serializers import UserSerializer


class UserView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserRegisterView(generics.CreateAPIView):
    model = User
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer

