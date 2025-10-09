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
    path("create/", views.create, name="create"),
    path("update/<int:id>/", views.update, name="update"),
    path("delete/<int:id>/", views.delete, name="delete"),
    path("project_detail/<int:id>/", views.project_detail, name="project_detail"),
    path("dashboard/<str:username>/", views.dashboard, name="dashboard"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
    path("star/<int:project_id>/", views.star, name='"star')
]
