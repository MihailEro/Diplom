import time

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, CallbackToken
from users.serializers import LoginSerializer, VerifyTokenSerializer, TokenResponseSerializer, ProfileSerializer
from users.services import send_sms_with_callback_token, create_authentication_token


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(CreateAPIView):

    queryset = User.objects.all()
    permission_classes = [AllowAny, ]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs) -> Response:

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        data = {
            "user": serializer.data,
            "next_page": f"http://127.0.0.1:8000/verify/{serializer.data['id']}"
        }

        if serializer.is_valid:
            user = User.objects.get(pk=serializer.data['id'])
            callback_token = CallbackToken.objects.filter(user=user).first()
            send_sms_with_callback_token(user, callback_token, **kwargs)

        time.sleep(2)

        return Response(data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyTokenView(APIView):

    serializer_class = VerifyTokenSerializer
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs) -> Response:

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            auth_token = create_authentication_token(user)

            if auth_token:
                token_serializer = TokenResponseSerializer(data={"token": auth_token.key, },
                                                           partial=True)
                if token_serializer.is_valid():
                    # Return our key for consumption.
                    return Response(token_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': "Couldn't log you in. Try again later."},
                            status=status.HTTP_400_BAD_REQUEST)


class ProfileView(RetrieveUpdateAPIView):

    queryset = User.objects.filter(is_active=True)
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self) -> User:

        return self.request.user

    @extend_schema(deprecated=True)
    def put(self, request, *args, **kwargs) -> None:

        raise NotImplementedError
