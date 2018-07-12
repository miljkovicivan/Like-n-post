from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.contrib.postgres.fields import JSONField

# Create your models here.

class TwoFA(models.Model):
    completed = models.BooleanField(default=False)
    user = models.OneToOneField(User, related_name='two_fa', on_delete=models.DO_NOTHING)
    secret = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now=True)


class UserAdditionalData(models.Model):
    user = models.OneToOneField(User, related_name='user_additional_data', on_delete=models.CASCADE)
    additional_data = JSONField(null=True)

class Post(models.Model):

    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    @cached_property
    def username(self):
        return self.owner.username

    class Meta:
        unique_together = ('owner', 'post')
