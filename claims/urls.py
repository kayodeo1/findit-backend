from django.urls import path
from .views import (
    ClaimListCreateView,
    ClaimDetailView,
    ClaimReviewView,
    ClaimHistoryView,
    AdminClaimListView,
)

urlpatterns = [
    path("", ClaimListCreateView.as_view()),
    path("all/", AdminClaimListView.as_view()),
    path("<int:pk>/", ClaimDetailView.as_view()),
    path("<int:pk>/review/", ClaimReviewView.as_view()),
    path("<int:pk>/history/", ClaimHistoryView.as_view()),
]
