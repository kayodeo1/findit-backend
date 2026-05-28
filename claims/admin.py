from django.contrib import admin
from .models import Claim, ReleaseRecord, StatusHistory


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ["id", "item", "owner", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["item__name", "owner__email"]


@admin.register(ReleaseRecord)
class ReleaseRecordAdmin(admin.ModelAdmin):
    list_display = ["claim", "admin", "release_date"]


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["claim", "old_status", "new_status", "changed_by", "timestamp"]
