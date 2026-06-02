from rest_framework import serializers
from .models import Claim, ReleaseRecord, StatusHistory


class ClaimSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    item_name = serializers.SerializerMethodField()
    item_status = serializers.SerializerMethodField()

    class Meta:
        model = Claim
        fields = [
            "id", "item", "item_name", "item_status", "owner", "owner_name",
            "proof", "status", "rejection_reason", "admin_query",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "owner", "status", "rejection_reason", "admin_query",
            "created_at", "updated_at",
        ]

    def get_owner_name(self, obj):
        return obj.owner.get_full_name() or obj.owner.username

    def get_item_name(self, obj):
        return obj.item.name

    def get_item_status(self, obj):
        return obj.item.status

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class ClaimReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)
    release_date = serializers.DateField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class ReleaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseRecord
        fields = ["id", "claim", "admin", "release_date", "notes"]
        read_only_fields = ["id", "admin"]


class StatusHistorySerializer(serializers.ModelSerializer):
    changed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StatusHistory
        fields = ["id", "old_status", "new_status", "changed_by", "changed_by_name", "timestamp"]

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return "System"
