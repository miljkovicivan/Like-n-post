from django.contrib.auth.models import User
from likenpost.apps.post.models import Post
from rest_framework import routers, serializers, viewsets

class PostSerializer(serializers.HyperlinkedModelSerializer):

    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return Post.objects.create(**validated_data)

    class Meta:
        model = Post
        fields = ('content', 'owner', 'url')

