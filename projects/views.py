import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import Review, User, Project, Tech


# Create your views here.

# Feed Page
def index(request):
    # Get all public projects, excluding the current user's if authenticated
    projects = Project.objects.filter(is_public=True)
    if request.user.is_authenticated:
        projects = projects.exclude(owner=request.user)

    projects = projects.order_by("-timestamp")
    return render(request, "projects/index.html", {"projects": projects})


# Create new project
@login_required
def create(request):
    if request.method == "POST":
        # Get project data
        title = request.POST["title"]
        overview = request.POST["overview"]
        description = request.POST["description"]
        video_url = request.POST["video"]
        image = request.FILES.get("file")
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
            is_public=True if status == "public" else False,
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
@csrf_exempt
@login_required
def update(request): ...


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
        return JsonResponse({"error": "DELETE request required."}, status=400)


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

    # Add unique authenticated viewer if they are not the owner
    if (
        request.user.is_authenticated
        and request.user != project.owner
        and project.is_public
    ):
        project.viewers.add(request.user)

    # Get project reviews
    reviews = Review.objects.filter(project=id)

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "key_learning": project.key_learning.splitlines(),
            "objectives": project.objectives.splitlines(),
            "techs": techs,
            "reviews": reviews,
        },
    )


@csrf_exempt
@login_required
def review(request, project_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request is required."})

    # Current project
    project = Project.objects.get(pk=project_id)
    if not project:
        return JsonResponse({"error": "Project Not Found."})

    # Load request content
    data = json.loads(request.body)
    if not data.get("content"):
        return JsonResponse({"message": "Empty review not allowed"})

    # Create new review
    review = Review.objects.create(
        user=request.user, project=project, content=data.get("content")
    )
    review.save()

    # Return new content
    return JsonResponse(
        {"message": "Comment added successfully.", "content": review.content},
        status=201,
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
    image = request.FILES["photo"]

    # Save the user image
    request.user.photo = image
    request.user.save()

    return JsonResponse({"message": "Image uploaded sucessfully."}, status=200)


@csrf_exempt
@login_required
def follow(request, user_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Handle follow/unfollow action
    user = User.objects.get(pk=user_id)
    if request.user in user.followers.all():
        user.followers.remove(request.user)
        user.save()
        return JsonResponse(
            {"message": "Unfollowed", "followers": user.followers.count()}, status=200
        )
    else:
        if user != request.user:
            user.followers.add(request.user)
            user.save()
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

    if request.user.is_authenticated:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found."}, status=404)

        if request.user in project.stars.all():
            project.stars.remove(request.user)
            return JsonResponse({"starred": False, "count": project.stars.count()}, status=200)
        else:
            project.stars.add(request.user)
            return JsonResponse({"starred": True, "count": project.stars.count()}, status=200)
    else:
        return JsonResponse({"error": "User not authenticated."}, status=403)


@csrf_exempt
@login_required
def visibility(request, project_id):
    # Allow only PUT request
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."})

    # Get the current project
    project = Project.objects.get(pk=project_id)

    # access request body
    data = json.loads(request.body)

    # Change visibility
    project.is_public = (data.get("visibility") == "public")

    # Save changes
    project.save()

    return JsonResponse({
        "message": "visibility changes successfully.",
        "is_public": project.is_public
        }, status=200)


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
