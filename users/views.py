from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, ProfileSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse


class RegisterView(APIView):
    """
    User registration endpoint.
    POST: Register a new user
    """
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['users'],
        summary="User Registration",
        description="Register a new user with email and password.",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "message": "User registered successfully"
                    }
                }
            ),
            400: OpenApiResponse(
                description="Validation error",
                examples={
                    "application/json": {
                        "email": ["This field may not be blank."],
                        "password": ["This field may not be blank."]
                    }
                }
            )
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User registered successfully'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    User profile endpoint.
    GET: Retrieve authenticated user's profile
    PUT: Update authenticated user's profile
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['users'],
        summary="Get User Profile",
        description="Retrieve the authenticated user's profile information.",
        responses={
            200: OpenApiResponse(
                description="User profile retrieved successfully",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe"
                    }
                }
            ),
            401: OpenApiResponse(
                description="Authentication required"
            )
        }
    )
    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)
    @extend_schema(
        tags=['users'],
        summary="Update User Profile",
        description="Update the authenticated user's profile information.",
        request=ProfileSerializer,
        responses={
            200: OpenApiResponse(
                description="Profile updated successfully",
                examples={
                    "application/json": {
                        "message": "Profile updated successfully",
                        "data": {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        }
                    }
                }
            ),
            400: OpenApiResponse(
                description="Validation error"
            ),
            401: OpenApiResponse(
                description="Authentication required"
            )
        }
    )
    def put(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Profile updated successfully', 'data': serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

