from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "phone"]
        read_only_fields = ["id", "email", "role"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserAdminSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name", "role", "phone", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
