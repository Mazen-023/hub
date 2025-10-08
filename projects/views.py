import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Project, Tech

# Create your views here.


def index(request):
    return render(request, "projects/index.html")


# Create new project
@login_required
def create(request):
    if request.method == "POST":
        # Get project data
        title = request.POST["title"]
        overview = request.POST["overview"]
        description = request.POST["description"]
        video_url = request.POST["video"]
        image = request.FILES["file"]
        objectives = request.POST["objectives"]
        key_learning = request.POST["key_learning"]
        status = request.POST["status"]

        # Get tech data
        tech = request.POST["tech"]

        # Save project data
        project = Project.objects.create(
            owner=request.user,
            title=title,
            overview=overview,
            description=description,
            video_url=video_url,
            image=image,
            objectives=objectives,
            key_learning=key_learning,
            is_public=True if status == "public" else "False",
        )

        # save tech data
        skills = tech.split(",")
        for name in skills:
            Tech.objects.create(project=project, name=name)

        return HttpResponseRedirect(
            reverse("projects:project_detail", args=[project.id])
        )

    else:
        return render(request, "projects/create.html")

# Update existing project
def update(request, id):
    return render(request, "projects/update.html")


# Delete existing project
@csrf_exempt
@login_required
def delete(request, id):
    if request.method == "DELETE":
        project = get_object_or_404(Project, id=id, owner=request.user)
       
        # Delete related tech objects
        Tech.objects.filter(project=project).delete()

        # Delete the project
        project.delete()

        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "DELETE request required."
        }, status=400)


# Display project detail
@login_required
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

    # Get tech by project
    techs = Tech.objects.filter(project=project)

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "key_learning": project.key_learning.splitlines(),
            "objectives": project.objectives.splitlines(),
            "techs": techs
        },
    )

@login_required
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
