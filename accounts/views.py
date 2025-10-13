from django.shortcuts import get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from projects.models import Project


from .models import User


def login_view(request):
    """
    Authenticate and log in an existing user.

    :param request: The HTTP request object containing user credentials.
    :return: HttpResponseRedirect to index template on successful login.
    :return: Rendered login template with error message on failure.
    """
    if request.method == "POST":
        # Sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back {user.username}!")
            return HttpResponseRedirect(reverse("projects:index"))
        else:
            messages.error(request, "Invalid username or password")
            return render(request, "accounts/login.html")
    else:
        return render(request, "accounts/login.html")


def logout_view(request):
    """
    Log out the currently authenticated user.

    :param request: The HTTP request object containing user session.
    :return: HttpResponseRedirect to index template.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return HttpResponseRedirect(reverse("projects:index"))


def register(request):
    """
    Create and register a new user account.

    :param request: The HTTP request object containing registration data.
    :raises IntegrityError: If the username is already taken.
    :return: HttpResponseRedirect to index template on successful registration.
    :return: Rendered register template with error message on failure.
    """
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # password validate
        if password != confirmation:
            messages.warning(request, "Passwords do not match.")
            return render(request, "accounts/register.html")

        # Attemp to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "That username is already taken.")
            return render(request, "accounts/register.html")

        # Logged the user in
        login(request, user)
        messages.success(request, "Your account has been created successfully!")
        return HttpResponseRedirect(reverse("projects:index"))
    else:
        return render(request, "accounts/register.html")


@login_required
def dashboard(request, username):
    """
    Display user profile with their projects and following status.

    :param request: The HTTP request object.
    :param username (string): Username of the profile to display.
    :raises Http404: If the user with the specified username doesn't exist.
    :return: Rendered dashboard template with user projects and profile data.
    """
    # Get user object
    user = get_object_or_404(User, username=username)

    # Get user projects
    projects = Project.objects.filter(owner=user)

    # Check if the user already follow or not
    is_following = request.user in user.followers.all()

    # Render user dashboard
    return render(
        request,
        "accounts/dashboard.html",
        {
            "projects": projects,
            "profile": user.serializer(),
            "is_following": is_following,
        },
    )


@csrf_exempt
@login_required
def update_photo(request):
    """
    Update the authenticated user's profile photo.

    :param request: The HTTP request object containing the uploaded image.
    :raises OSError: If the uploaded file is not a valid image.
    :return: JsonResponse with success message and status 200 on success.
    :return: JsonResponse with error message and status 400 on failure.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST request is required."}, status=400)

    # Get the image file from the client-side
    image = request.FILES.get("photo")
    if not image:
        return JsonResponse({"error": "No image file provided."}, status=400)

    # Save image if it's valid
    try:
        from PIL import Image

        with Image.open(image):
            request.user.photo = image
            request.user.save()
            return JsonResponse({"message": "Image uploaded successfully."}, status=200)
    except OSError:
        return JsonResponse({"error": "Unsupported file."}, status=400)


@csrf_exempt
@login_required
def follow(request, pk):
    """
    Handle user follow/unfollow functionality.

    :param request: The HTTP request objects containing user data.
    :param pk (int): Primary key of the user to follow/unfollow.
    :raises Http404: If the user with the specified pk doesn't exist.
    :return: A JsonResponse Contains success/error message and updated followers count.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Validate current user
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)

    # Handle follow/unfollow action
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
