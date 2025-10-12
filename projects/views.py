import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import ProjectForm

from .models import User, Project, Technology, Review


# Feed Page
def index(request):
    # Get all public projects, excluding the current user's if authenticated
    projects = Project.objects.filter(is_public=True)
    if request.user.is_authenticated:
        projects = projects.exclude(owner=request.user)

    return render(request, "projects/index.html", {"projects": projects})


# Create new project
@login_required
def create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.is_public = form.cleaned_data["is_public"] == "True"
            project.save()

            # Process technologies
            tech_string = form.cleaned_data.get("technologies", "")
            if tech_string:
                tech_names = [
                    name.strip() for name in tech_string.split(",") if name.strip()
                ]
                for name in tech_names:
                    tech, created = Technology.objects.get_or_create(name=name)
                    project.technologies.add(tech)

            return HttpResponseRedirect(
                reverse("projects:project_detail", args=[project.id])
            )
    else:
        # For GET requests, show empty form
        form = ProjectForm()
        return render(request, "projects/create.html", {"form": form})


# Update existing project
@login_required
def update(request, id):
    # Get the project and verify ownership
    project = get_object_or_404(Project, id=id, owner=request.user)

    if request.method == "POST":
        # Initialize form with POST data, FILES and existing project instance
        form = ProjectForm(request.POST, request.FILES, instance=project)

        if form.is_valid():
            project = form.save(commit=False)
            project.is_public = form.cleaned_data["is_public"] == "True"
            project.save()

            # Process technologies
            project.technologies.clear()
            tech_string = form.cleaned_data.get("technologies", "")
            if tech_string:
                tech_names = [
                    name.strip() for name in tech_string.split(",") if name.strip()
                ]
                for name in tech_names:
                    tech, created = Technology.objects.get_or_create(name=name)
                    project.technologies.add(tech)

            return HttpResponseRedirect(
                reverse("projects:project_detail", args=[project.id])
            )
    else:
        initial_data = {
            "technologies": ", ".join(
                [tech.name for tech in project.technologies.all()]
            )
        }
        form = ProjectForm(instance=project, initial=initial_data)

    return render(request, "projects/update.html", {"form": form, "project": project})


# Delete existing project
@csrf_exempt
@login_required
def delete(request, id):
    if request.method == "DELETE":
        project = get_object_or_404(Project, id=id, owner=request.user)
        project.delete()
        return HttpResponse(status=204)
    else:
        return JsonResponse({"error": "DELETE request required."}, status=400)


# Display project detail
@login_required
def project_detail(request, id):
    # Get project
    project = get_object_or_404(Project, id=id)

    # Add unique viewer if they are not the owner
    if request.user not in project.viewers.all() and request.user != project.owner:
        project.viewers.add(request.user)

    return render(request, "projects/project_detail.html", {"project": project})


@csrf_exempt
@login_required
def review(request, project_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request is required."}, status=400)

    # Get the project or return a 404 error
    project = get_object_or_404(Project, pk=project_id)

    # Load and validate the review content
    data = json.loads(request.body)
    content = data.get("content")
    if not content or len(content) > 1000:
        return JsonResponse(
            {"error": "Review must be between 1 and 1000 characters."}, status=400
        )

    # Create the new review
    Review.objects.create(user=request.user, project=project, content=content)

    # Return a success response
    return JsonResponse({"message": "Review added successfully."}, status=201)


@login_required
def dashboard(request, username):
    # Get user object
    user = get_object_or_404(User, username=username)

    # Get user projects
    projects = Project.objects.filter(owner=user)

    # Check if the user already follow or not
    is_following = request.user in user.followers.all()

    # Render user dashboard
    return render(
        request,
        "projects/dashboard.html",
        {
            "projects": projects,
            "profile": user.serializer(),
            "is_following": is_following,
        },
    )


@csrf_exempt
@login_required
def update_photo(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request is required."})

    # Get the image file from the client-side
    image = request.FILES.get("photo")
    if image:
        from PIL import Image

        try:
            with Image.open(image):
                request.user.photo = image
                request.user.save()
        except OSError:
            return JsonResponse({"error": "Unsupported file."})
        return JsonResponse({"message": "Image uploaded sucessfully."}, status=200)


@csrf_exempt
@login_required
def follow(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Handle follow/unfollow action
    user = get_object_or_404(User, pk=user_id)
    if user is not request.user:
        if request.user in user.followers.all():
            user.followers.remove(request.user)
            return JsonResponse(
                {"message": "Unfollowed", "followers": user.followers.count()},
                status=200,
            )
        else:
            user.followers.add(request.user)
            return JsonResponse(
                {"message": "Followed", "followers": user.followers.count()}, status=200
            )
    else:
        return JsonResponse({"message": "Cannot follow yourself."}, status=400)


@csrf_exempt
@login_required
def star(request, project_id):
    # Toggle star via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check if the project exists
    project = get_object_or_404(Project, pk=project_id)

    # Toggle between star and starred
    if request.user in project.stars.all():
        project.stars.remove(request.user)
        return JsonResponse(
            {"starred": False, "count": project.stars.count()}, status=200
        )
    else:
        project.stars.add(request.user)
        return JsonResponse(
            {"starred": True, "count": project.stars.count()}, status=200
        )


@csrf_exempt
@login_required
def visibility(request, project_id):
    # Allow only PUT request
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=405)

    # Get the current project
    project = get_object_or_404(Project, pk=project_id)

    # Check if the request user is the owner
    if not request.user == project.owner:
        return JsonResponse(
            {"error": "You don't have permission to edit this project"}, status=403
        )

    # access request body
    data = json.loads(request.body)

    # Change visibility
    project.is_public = data.get("visibility") == "public"

    # Save changes
    project.save()

    return JsonResponse(
        {"message": "visibility changes successfully.", "is_public": project.is_public},
        status=200,
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
