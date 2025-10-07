from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="add"),
    path("project_detail/<int:id>", views.project_detail, name="project_detail"),
]
