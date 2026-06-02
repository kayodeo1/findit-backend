from django.conf import settings
from django.db import models


class Claim(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    item = models.ForeignKey(
        "items.Item", on_delete=models.CASCADE, related_name="claims"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="claims"
    )
    proof = models.TextField(help_text="Proof of ownership description")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    admin_query = models.TextField(
        blank=True, help_text="Question the admin raises with the claimant while reviewing"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Claim #{self.pk} — {self.item.name} by {self.owner}"


class ReleaseRecord(models.Model):
    claim = models.OneToOneField(Claim, on_delete=models.CASCADE, related_name="release_record")
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="releases"
    )
    release_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Release for claim #{self.claim_id}"


class StatusHistory(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name="history")
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
