from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property

# Create your models here.

class Post(models.Model):

    content = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class Like(models.Model):
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    @cached_property
    def username(self):
        return self.owner.username

    class Meta:
        unique_together = ('owner', 'post')
