from rest_framework import generics, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import Item
from .serializers import ItemSerializer
from utils.permissions import IsAdmin


class ItemListCreateView(generics.ListCreateAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "color"]
    search_fields = ["name", "description", "color", "location"]
    ordering_fields = ["date", "created_at"]

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get("status")
        qs = Item.objects.select_related("reported_by")

        if user.role == "admin":
            return qs.all()

        if status_filter:
            return qs.filter(status=status_filter)

        if user.role == "owner":
            from django.db.models import Q
            return qs.filter(Q(reported_by=user) | Q(status="found"))

        return qs.all()

    def perform_create(self, serializer):
        user = self.request.user
        status = self.request.data.get("status")

        if user.role == "owner" and status != "lost":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Owners can only report lost items.")

        if user.role == "finder" and status != "found":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Finders can only report found items.")

        serializer.save(reported_by=user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Item.objects.select_related("reported_by").all()
        return Item.objects.select_related("reported_by").all()


class AdminItemListView(generics.ListAPIView):
    queryset = Item.objects.select_related("reported_by").all()
    serializer_class = ItemSerializer
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "color"]
    search_fields = ["name", "description", "location"]
