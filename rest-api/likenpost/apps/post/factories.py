from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from likenpost.apps.post.models import Post, Like
from factory import sequence


class UserFactory(DjangoModelFactory):

    username = sequence(lambda x: 'User %d' % x)

    class Meta:
        model = User


class PostFactory(DjangoModelFactory):

    content = sequence(lambda x: 'Content %d' % x)

    class Meta:
        model = Post


class LikeFactory(DjangoModelFactory):

    class Meta:
        model = Like
