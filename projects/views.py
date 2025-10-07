from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Project, User

# Create your views here.


def index(request):
    return render(request, "projects/index.html")


def add(request):
    return render(request, "projects/add.html")


def project_detail(request, id):
    # Get project
    try:
        project = Project.objects.get(id=id)
    except Project.DoesNotExist:
        return render(
            request,
            "projects/project_detail.html",
            {"message": "Project doesn't exist"},
        )

    return render(request, "projects/project_detail.html", {"project": project})


def dashboard(request, username):
    # Get user object
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return render(
            request, "projects/dashbaord.html", {"message": "user is not exist"}
        )

    # Get user projects
    projects = Project.objects.filter(owner=user)

    # Render user dashboard
    return render(
        request,
        "projects/dashboard.html",
        {"projects": projects, "profile": user.serializer()},
    )


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
                "projects/login.html",
                {"message": "Invalid username or password"},
            )
    else:
        return render(request, "projects/login.html")


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
                request, "projects/register.html", {"message": "Password must match."}
            )

        # Create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "projects/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("projects:index"))
    else:
        return render(request, "projects/register.html")
