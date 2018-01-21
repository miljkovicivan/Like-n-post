from rest_framework import viewsets, response, generics, permissions
from django.contrib.auth.models import User
from likenpost.apps.post.serializers import PostSerializer, UserSerializer, UserAdditionalDataSerializer
from likenpost.apps.post.models import Post, Like, UserAdditionalData
from rest_framework.decorators import detail_route, list_route
import clearbit
from django.conf import settings


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = User.objects.all()
        if self.request.method in ['PUT', 'DELETE']:
            queryset = queryset.filter(pk=self.request.user.pk)
        return queryset

    def perform_create(self, serializer):

        user = serializer.save()

        clearbit.key = settings.CLEARBIT_KEY
        additional_data = clearbit.Enrichment.find(email=user.email, stream=True)

        UserAdditionalData.objects.create(user=user, additional_data=additional_data)


class UserAdditionalDataViewSet(viewsets.ModelViewSet):
    serializer_class = UserAdditionalDataSerializer

    def get_queryset(self):
        queryset = UserAdditionalData.objects.all()
        if self.request.method in ['PUT', 'DELETE']:
            queryset = queryset.filter(user=self.request.user)
        return queryset


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

    @list_route(methods=['get'])
    def myposts(self, request):

        queryset = Post.objects.filter(owner=request.user)

        serializer = self.get_serializer(queryset, many=True)

        return response.Response(serializer.data)

    @list_route(methods=['get'])
    def newposts(self, request):

        queryset = Post.objects.exclude(owner=request.user)

        serializer = self.get_serializer(queryset, many=True)

        return response.Response(serializer.data)
