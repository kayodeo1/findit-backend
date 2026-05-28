import datetime
import logging

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)

TOKEN_LIFETIME_DAYS = 30


def make_token(user) -> str:
    payload = {
        "sub": str(user.pk),
        "email": user.email,
        "role": user.role,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=TOKEN_LIFETIME_DAYS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


class LocalJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ", 1)[1].strip()
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.PyJWTError as exc:
            logger.warning("JWT decode failed: %s", exc)
            raise AuthenticationFailed("Invalid token.")

        User = get_user_model()
        try:
            user = User.objects.get(pk=int(payload["sub"]))
        except (User.DoesNotExist, ValueError, KeyError):
            raise AuthenticationFailed("User not found.")

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


# Keep old name as alias so settings.py reference still works
SupabaseAuthentication = LocalJWTAuthentication


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == "admin")


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in ("owner", "admin"))


class IsFinder(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in ("finder", "admin"))
