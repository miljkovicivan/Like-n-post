from rest_framework import viewsets, response, generics
from django.contrib.auth.models import User
from likenpost.apps.post.serializers import PostSerializer
from likenpost.apps.post.models import Post, Like
from rest_framework.decorators import detail_route


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = Post.objects.all()
        if self.request.method in ['PUT', 'DELETE']:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


    @detail_route(methods=['post'])
    def like(self, request, pk=None):

        post = self.get_object()

        f = filter(lambda x: x.owner == request.user, post.likes.all())
        l = list(f)

        if len(l) != 0:
            return response.Response(
                status=400, data='Already liked'
            )

        Like.objects.create(owner=request.user, post=post)

        return response.Response(
            status=200, data='OK'
        )

    @detail_route(methods=['post'])
    def unlike(self, request, pk=None):

        post = self.get_object()

        f = filter(lambda x: x.owner == request.user, post.likes.all())
        l = list(f)

        if len(l) == 0:
            return response.Response(
                status=400, data='You have to like the post first.'
            )

        Like.objects.get(owner=request.user, post=post).delete()

        return response.Response(
            status=200, data='OK'
        )

