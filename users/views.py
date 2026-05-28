from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .serializers import UserProfileSerializer, UserAdminSerializer
from utils.permissions import IsAdmin, make_token


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password", "")
        full_name = (request.data.get("full_name") or "").strip()
        role = request.data.get("role", "owner")

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=400)

        if role not in User.SELF_SERVICE_ROLES:
            role = "owner"

        if User.objects.filter(email=email).exists():
            return Response({"detail": "An account with this email already exists."}, status=400)

        first_name, _, last_name = full_name.partition(" ")
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )

        token = make_token(user)
        return Response(
            {"token": token, "user": UserProfileSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password", "")

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=400)

        # Django's authenticate needs the username field
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({"detail": "Invalid email or password."}, status=401)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response({"detail": "Invalid email or password."}, status=401)

        token = make_token(user)
        return Response({"token": token, "user": UserProfileSerializer(user).data})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["role"]


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdmin]
