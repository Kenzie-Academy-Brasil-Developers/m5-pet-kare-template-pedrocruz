from django.urls import path
from .views import PetsDetailView, PetsView

urlpatterns = [
    path("pets/", PetsView.as_view()),
    path("pets/<int:pet_id>/", PetsDetailView.as_view()),
]