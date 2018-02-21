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

        if 'bot' in self.request.query_params.keys():
            return

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







import datetime
import pyotp
import pytz

from rest_framework.decorators import api_view, permission_classes
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.views import APIView

from likenpost.apps.post.models import TwoFA


class Enable2FA(APIView):

    def post(self, request, *args, **kwargs):

        secret = pyotp.random_base32()

        totp = pyotp.TOTP(secret)

        if TwoFA.objects.filter(user=request.user).exists():
            return response.Response({'error': 'Alredy enabled'})


        TwoFA.objects.create(user=request.user, secret=secret)

        qr_code = totp.provisioning_uri(request.data['username'], issuer_name="TradeCore")

        return response.Response({'qr_code': qr_code})

enable_2fa = Enable2FA.as_view()


class Disable2FA(APIView):

    def post(self, request, *args, **kwargs):

        if TwoFA.objects.filter(user=request.user).exists():
            TwoFA.objects.filter(user=request.user).delete()
            return response.Response({'2fa': 'disabled'})
        else:
            return response.Response({'2fa': 'already disabled'})

disable_2fa = Disable2FA.as_view()


TIME_FOR_COMPLETION = datetime.timedelta(seconds=60)
class Complete2FA(APIView):


    def post(self, request, *args, **kwargs):

        two_fa = TwoFA.objects.filter(user=request.user).first()  # safe get
        if two_fa is None:
            return response.Response({'error': 'Enable 2FA first'})

        now = datetime.datetime.now().replace(tzinfo=pytz.UTC)

        if now - two_fa.created_at > TIME_FOR_COMPLETION:
            two_fa.delete()
            return response.Response({'2fa': 'Please enable 2fa again for security reason'})

        totp = pyotp.TOTP(two_fa.secret)

        if totp.verify(request.data['code']):
            two_fa.completed = True
            two_fa.save()
            return response.Response({'2fa': 'completed'})
        else:
            return response.Response({'2fa': 'wrong code'})

complete_2fa = Complete2FA.as_view()


class Login(APIView):

    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):

        user = User.objects.filter(username=request.data['username']).first()
        two_fa = TwoFA.objects.filter(user=user).first()
        code = request.data.get('code', None)

        if two_fa:
            # 2fa is enabled
            if two_fa.completed:
                totp = pyotp.TOTP(two_fa.secret)
                if totp.verify(code):
                    return obtain_jwt_token(request._request)
            return response.Response({'error': 'Not ok'})
        else:
            return obtain_jwt_token(request._request)


login = Login.as_view()
