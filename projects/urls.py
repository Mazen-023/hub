from django.urls import path

from . import views

# Create your urls here.

app_name = "projects"

urlpatterns = [
    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    # Projects
    path("", views.index, name="index"),
    path("add", views.add, name="add"),
    path("project_detail/<int:id>", views.project_detail, name="project_detail"),
    path("dashboard/<str:username>", views.dashboard, name="dashboard"),
]
