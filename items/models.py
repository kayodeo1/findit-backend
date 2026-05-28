from django.conf import settings
from django.db import models


class Item(models.Model):
    class Status(models.TextChoices):
        LOST = "lost", "Lost"
        FOUND = "found", "Found"
        CLAIMED = "claimed", "Claimed"

    name = models.CharField(max_length=255)
    description = models.TextField()
    color = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices)
    image = models.ImageField(upload_to="items/", blank=True, null=True)
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"
