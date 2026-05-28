from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.SerializerMethodField()
    reported_by_role = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id", "name", "description", "color", "location", "date",
            "status", "image", "image_url",
            "reported_by", "reported_by_name", "reported_by_role",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "reported_by", "created_at", "updated_at"]
        extra_kwargs = {"image": {"write_only": True, "required": False}}

    def get_reported_by_name(self, obj):
        return obj.reported_by.get_full_name() or obj.reported_by.username

    def get_reported_by_role(self, obj):
        return obj.reported_by.role

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def create(self, validated_data):
        validated_data["reported_by"] = self.context["request"].user
        return super().create(validated_data)
