from django.contrib.auth.models import User
from likenpost.apps.post.models import Post, Like, UserAdditionalData
from rest_framework import routers, serializers, viewsets
from django.contrib.auth.hashers import make_password


class PostSerializer(serializers.ModelSerializer):

    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    likes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username'
    )

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return Post.objects.create(**validated_data)

    class Meta:
        model = Post
        fields = ('id', 'content', 'owner', 'likes')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'first_name', 'last_name', 'email', 'password', 'user_additional_data')
        read_only_fields = ('user_additional_data',)
        extra_kwargs = {'password': {'write_only': True}}

    def prepare_password(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)
        return validated_data

    def create(self, validated_data):
        validated_data = self.prepare_password(validated_data)
        return super(UserSerializer, self).create(validated_data)

    def update(self, obj, validated_data):
        validated_data = self.prepare_password(validated_data)
        return super(UserSerializer, self).update(obj, validated_data)

class UserAdditionalDataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserAdditionalData
        fields = '__all__'

