from django.contrib import admin
from .models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "color", "location", "date", "reported_by"]
    list_filter = ["status", "color"]
    search_fields = ["name", "description", "location"]
