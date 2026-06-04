from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from .serializers import UserProfileSerializer, UserAdminSerializer
from utils.permissions import IsAdmin, make_token


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        email = (data.get("email") or "").strip().lower()
        password = data.get("password", "")
        role = data.get("role", "owner")

        # Names: accept discrete fields, fall back to a single full_name.
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        middle_name = (data.get("middle_name") or "").strip()
        if not first_name and not last_name:
            full_name = (data.get("full_name") or "").strip()
            first_name, _, last_name = full_name.partition(" ")

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=400)

        if not first_name:
            return Response({"detail": "First name is required."}, status=400)

        if role not in User.SELF_SERVICE_ROLES:
            role = "owner"

        if User.objects.filter(email=email).exists():
            return Response({"detail": "An account with this email already exists."}, status=400)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            middle_name=middle_name,
            phone=(data.get("phone") or "").strip(),
            house_no=(data.get("house_no") or "").strip(),
            street=(data.get("street") or "").strip(),
            area=(data.get("area") or "").strip(),
            lga=(data.get("lga") or "").strip(),
            city=(data.get("city") or "").strip(),
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

        # The role is chosen at sign-in: a single account can act as either an
        # owner or a finder. Switch the active role to match the selection
        # (admins keep their role and are never downgraded).
        role = (request.data.get("role") or "").strip().lower()
        if role in User.SELF_SERVICE_ROLES and user.role != "admin" and user.role != role:
            user.role = role
            user.save(update_fields=["role"])

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
    # Admin can only search *users* (not items) — name, email, phone, location.
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["role", "is_flagged"]
    search_fields = [
        "first_name", "middle_name", "last_name", "email", "phone",
        "city", "area", "lga",
    ]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: view/flag/delete a user. Deleting removes the account but does
    not otherwise 'harm' the person — their reported items are cascade-removed."""
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAdmin]

    def perform_destroy(self, instance):
        if instance.role == "admin":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Admin accounts cannot be deleted here.")
        instance.delete()
