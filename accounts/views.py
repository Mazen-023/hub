from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User


# Create your views here.
def login_view(request):
    if request.method == "POST":
        # Sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("projects:index"))
        else:
            return render(
                request,
                "accounts/login.html",
                {"message": "Invalid username or password"},
            )
    else:
        return render(request, "accounts/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("projects:index"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]

        # password validate
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not password == confirmation:
            return render(
                request, "accounts/register.html", {"message": "Password must match."}
            )

        # Create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "accounts/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("projects:index"))
    else:
        return render(request, "accounts/register.html")


def dashboard(request):
    return render(request, "accounts/dashboard.html")
