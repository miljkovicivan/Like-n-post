from rest_framework import viewsets, response
from django.contrib.auth.models import User
from likenpost.apps.post.serializers import PostSerializer
from likenpost.apps.post.models import Post


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def post(self, request, *args, **kwargs):
        import pdb; pdb.set_trace()

        return response.Response()
