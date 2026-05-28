from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from items.models import Item
from .models import Claim, ReleaseRecord, StatusHistory
from .serializers import ClaimSerializer, ClaimReviewSerializer, StatusHistorySerializer
from utils.permissions import IsAdmin


class ClaimListCreateView(generics.ListCreateAPIView):
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Claim.objects.select_related("item", "owner").all()
        return Claim.objects.select_related("item", "owner").filter(owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        item_id = self.request.data.get("item")
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Item not found.")

        if item.status != "found":
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Can only claim items with 'found' status.")

        if Claim.objects.filter(item=item, owner=user, status="pending").exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You already have a pending claim for this item.")

        serializer.save(owner=user)


class ClaimDetailView(generics.RetrieveAPIView):
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Claim.objects.select_related("item", "owner").all()
        return Claim.objects.select_related("item", "owner").filter(owner=user)


class ClaimReviewView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            claim = Claim.objects.select_related("item", "owner").get(pk=pk)
        except Claim.DoesNotExist:
            return Response({"detail": "Claim not found."}, status=status.HTTP_404_NOT_FOUND)

        if claim.status != "pending":
            return Response(
                {"detail": "Only pending claims can be reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ClaimReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        old_status = claim.status

        if data["action"] == "approve":
            claim.status = "approved"
            claim.item.status = "claimed"
            claim.item.save(update_fields=["status"])

            ReleaseRecord.objects.create(
                claim=claim,
                admin=request.user,
                release_date=data.get("release_date", timezone.now().date()),
                notes=data.get("notes", ""),
            )
        else:
            claim.status = "rejected"
            claim.rejection_reason = data.get("rejection_reason", "")

        claim.save()

        StatusHistory.objects.create(
            claim=claim,
            old_status=old_status,
            new_status=claim.status,
            changed_by=request.user,
        )

        return Response(ClaimSerializer(claim).data)


class ClaimHistoryView(generics.ListAPIView):
    serializer_class = StatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        claim_id = self.kwargs["pk"]
        user = self.request.user
        if user.role == "admin":
            return StatusHistory.objects.filter(claim_id=claim_id)
        return StatusHistory.objects.filter(claim_id=claim_id, claim__owner=user)


class AdminClaimListView(generics.ListAPIView):
    queryset = Claim.objects.select_related("item", "owner").all()
    serializer_class = ClaimSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]
