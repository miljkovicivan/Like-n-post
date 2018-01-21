from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from likenpost.apps.post.models import Post, Like, UserAdditionalData
import factory

class UserAdditionalDataFactory(DjangoModelFactory):
    additional_data = None

    class Meta:
        model = UserAdditionalData

class UserFactory(DjangoModelFactory):

    username = factory.Faker('user_name')
    password = factory.Faker('password')
    email = factory.Faker("email")
    user_additional_data = factory.RelatedFactory(UserAdditionalDataFactory, 'user')
    is_staff = False
    is_active = True

    class Meta:
        model = User


class PostFactory(DjangoModelFactory):

    content = factory.sequence(lambda x: 'Content %d' % x)

    class Meta:
        model = Post


class LikeFactory(DjangoModelFactory):

    class Meta:
        model = Like
