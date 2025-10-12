from django.urls import path

from . import views


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
    path("star/<int:project_id>/", views.star, name='"star'),
    path("reviews/<int:project_id>/", views.review, name="review"),
    path("visibility/<int:project_id>/", views.visibility, name="visibility"),
    # Users
    path("dashboard/<str:username>/", views.dashboard, name="dashboard"),
    path("update_photo/", views.update_photo, name="update_photo"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
]
