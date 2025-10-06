from django.urls import path

from . import views

app_name = "projects"
urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="add"),
    path("project/<int:id>", views.project_detial, name="project_detial"),
]