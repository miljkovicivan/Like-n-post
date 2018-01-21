from django.contrib import admin
from likenpost.apps.post import models

admin.site.register(models.UserAdditionalData)
admin.site.register(models.Post)
admin.site.register(models.Like)
