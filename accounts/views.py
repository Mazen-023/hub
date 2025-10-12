from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from projects.models import Project


from .models import User

# Login existing user
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


# Logout user
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("projects:index"))


# Register new user
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



# User dashboard
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

# Update user image
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


# Following system 
@csrf_exempt
@login_required
def follow(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Handle follow/unfollow action
    user = get_object_or_404(User, pk=pk)
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
