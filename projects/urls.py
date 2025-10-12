from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.index, name="index"),

    # API Routes
    path("project/create/", views.create, name="create"),
    path("project/<int:pk>/update/", views.update, name="update"),
    path("project/<int:pk>/delete/", views.delete, name="delete"),
    path("project/<int:pk>/detail/", views.detail, name="detail"),
    path("project/<int:pk>/stars/", views.stars, name="stars"),
    path("project/<int:pk>/reviews/", views.reviews, name="reviews"),
    path("project/<int:pk>/visibility/", views.visibility, name="visibility"),
]
