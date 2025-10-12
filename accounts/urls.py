from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/<str:username>/", views.dashboard, name="dashboard"),
    path("update_photo/", views.update_photo, name="update_photo"),
    path("follow/<int:user_id>/", views.follow, name="follow"),
]