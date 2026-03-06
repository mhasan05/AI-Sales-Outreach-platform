from django.contrib.auth import logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer


class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully.",
                    "token": token.key,
                    "data": UserProfileSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "status": "success",
                    "message": "Login successful.",
                    "token": token.key,
                    "data": UserProfileSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LogoutAPIView(APIView):
    def post(self, request):
        if request.auth:
            request.auth.delete()
        logout(request)

        return Response(
            {
                "status": "success",
                "message": "Logout successful.",
            },
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "success",
                "data": UserProfileSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )