from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["email", "first_name", "last_name", "role", "date_joined"]
    list_filter = ["role"]
    fieldsets = UserAdmin.fieldsets + (
        ("App Info", {"fields": ("role", "phone", "supabase_uid")}),
    )
