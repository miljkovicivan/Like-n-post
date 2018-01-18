from django.contrib.auth.models import User
from likenpost.apps.post.models import Post
from rest_framework import routers, serializers, viewsets

class PostSerializer(serializers.HyperlinkedModelSerializer):

    user = serializers.HyperlinkedRelatedField(
        read_only=True,
        many=False,
        view_name='user:user'
    )

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return Post.objects.create(**validated_data)

    class Meta:
        model = Post
        fields = ('content', 'user', 'url')

