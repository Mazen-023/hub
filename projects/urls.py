from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.index, name="index"),
    path("create/", views.create, name="create"),
    path("update/<int:id>/", views.update, name="update"),
    path("delete/<int:id>/", views.delete, name="delete"),
    path("project_detail/<int:id>/", views.project_detail, name="project_detail"),
    path("star/<int:project_id>/", views.star, name='"star'),
    path("reviews/<int:project_id>/", views.review, name="review"),
    path("visibility/<int:project_id>/", views.visibility, name="visibility"),
]
