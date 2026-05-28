from django.urls import path
from .views import ItemListCreateView, ItemDetailView, AdminItemListView

urlpatterns = [
    path("", ItemListCreateView.as_view()),
    path("<int:pk>/", ItemDetailView.as_view()),
    path("all/", AdminItemListView.as_view()),
]
