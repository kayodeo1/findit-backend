from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    address = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "middle_name", "last_name", "full_name",
            "role", "phone", "house_no", "street", "area", "lga", "city", "address",
        ]
        read_only_fields = ["id", "email", "role"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserAdminSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    address = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "middle_name", "last_name", "full_name",
            "role", "phone", "address", "is_flagged", "flag_reason",
            "date_joined", "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login"]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
