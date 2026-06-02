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
    middle_name = models.CharField(max_length=150, blank=True)

    # Address
    house_no = models.CharField(max_length=50, blank=True)
    street = models.CharField(max_length=255, blank=True)
    area = models.CharField(max_length=255, blank=True)
    lga = models.CharField("Local Government Area", max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)

    # Admin moderation
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)

    supabase_uid = models.CharField(
        max_length=255, unique=True, null=True, blank=True, db_index=True
    )

    @property
    def address(self) -> str:
        parts = [self.house_no, self.street, self.area, self.lga, self.city]
        return ", ".join(p for p in parts if p)

    def __str__(self) -> str:
        return self.get_username()
