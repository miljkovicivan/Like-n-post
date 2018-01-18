from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets


class UserSerializer(serializers.HyperlinkedModelSerializer):

    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'password', 'confirm_password')

