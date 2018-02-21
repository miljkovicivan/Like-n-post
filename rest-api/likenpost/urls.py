"""likenpost URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import routers
from likenpost.apps.post import views
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token

router = routers.DefaultRouter()

router.register('post', views.PostViewSet, base_name='post')
router.register('user', views.UserViewSet, base_name='user')
router.register('useradditionaldata', views.UserAdditionalDataViewSet, base_name='useradditionaldata')


urlpatterns = router.urls + [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),

    url(r'^api/2fa/complete/', views.complete_2fa),
    url(r'^api/2fa/enable/', views.enable_2fa),
    url(r'^api/2fa/disable/', views.disable_2fa),

    url(r'^api/login/', views.login),
    url(r'^api/post/', include('likenpost.apps.post.urls', namespace='post')),
]

if 'silk' in settings.INSTALLED_APPS:
    urlpatterns += [
        url(r'^silk/', include('silk.urls', namespace='silk'))
    ]

