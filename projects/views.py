import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .forms import ProjectForm

from .models import Project, Technology, Review


# Feed Page
def index(request):
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
            technologies = form.cleaned_data.get("technologies", "")
            if technologies:
                skills = [
                    name.strip() for name in technologies.split(",") if name.strip()
                ]
                for name in skills:
                    technology, created = Technology.objects.get_or_create(name=name)
                    project.technologies.add(technology)

            messages.success(
                request, f"Project '{project.title}' have been created successfully!"
            )
            return HttpResponseRedirect(reverse("projects:detail", args=[project.id]))
    else:
        # For GET requests, show empty form
        form = ProjectForm()
        return render(request, "projects/create.html", {"form": form})


# Update existing project
@login_required
def update(request, pk):
    # Get the project and verify ownership
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        # Initialize form with POST data, FILES and existing project instance
        form = ProjectForm(request.POST, request.FILES, instance=project)

        if form.is_valid():
            project = form.save(commit=False)
            project.is_public = form.cleaned_data["is_public"] == "True"
            project.save()

            # Process technologies
            project.technologies.clear()
            technologies = form.cleaned_data.get("technologies", "")
            if technologies:
                skills = [
                    name.strip() for name in technologies.split(",") if name.strip()
                ]
                for name in skills:
                    technology, created = Technology.objects.get_or_create(name=name)
                    project.technologies.add(technology)

            messages.success(
                request, f"Project '{project.title}' was updated successfully!"
            )
            return HttpResponseRedirect(reverse("projects:detail", args=[project.id]))
    else:
        technologies = {
            "technologies": ", ".join(
                [tech.name for tech in project.technologies.all()]
            )
        }
        form = ProjectForm(instance=project, initial=technologies)
        return render(
            request, "projects/update.html", {"form": form, "project": project}
        )


# Delete existing project
@csrf_exempt
@login_required
def delete(request, pk):
    if request.method == "DELETE":
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        project.delete()
        return HttpResponse(status=204)
    else:
        return JsonResponse({"error": "DELETE request required."}, status=400)


# Display project detail
@login_required
def detail(request, pk):
    # Get project
    project = get_object_or_404(Project, pk=pk)

    # Return a 403 Forbidden error if they don't have permission.
    if not project.is_public and request.user != project.owner:
        return HttpResponse(
            "You do not have permission to view this project.", status=403
        )

    # Add unique viewer if they are not the owner
    if request.user not in project.viewers.all() and request.user != project.owner:
        project.viewers.add(request.user)

    return render(request, "projects/detail.html", {"project": project})


@csrf_exempt
@login_required
def reviews(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST request is required."}, status=400)

    # Get the project or return a 404 error
    project = get_object_or_404(Project, pk=pk)

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


@csrf_exempt
@login_required
def stars(request, pk):
    # Toggle star via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    # Check if the project exists
    project = get_object_or_404(Project, pk=pk)

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
def visibility(request, pk):
    # Allow only PUT request
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."}, status=405)

    # Get the current project
    project = get_object_or_404(Project, pk=pk)

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
