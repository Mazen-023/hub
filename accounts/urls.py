from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    
    # API Routes
    path("user/<str:username>/dashboard/", views.dashboard, name="dashboard"),
    path("user/update_photo/", views.update_photo, name="update_photo"),
    path("user/<int:pk>/follow/", views.follow, name="follow"),
]