from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        OWNER = "owner", "Owner"
        FINDER = "finder", "Finder"

    SELF_SERVICE_ROLES = {"owner", "finder"}

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OWNER)
    phone = models.CharField(max_length=20, blank=True)
    supabase_uid = models.CharField(
        max_length=255, unique=True, null=True, blank=True, db_index=True
    )

    def __str__(self) -> str:
        return self.get_username()
