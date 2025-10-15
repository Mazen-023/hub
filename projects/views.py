import json
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.paginator import Paginator


from .forms import ProjectForm

from .models import Project, Technology, Review


def index(request):
    """
    Display public projects in the main feed.

    :param request: The HTTP request object.
    :return: Rendered index template with public projects.
    """
    projects = Project.objects.filter(is_public=True)
    if request.user.is_authenticated:
        projects = projects.exclude(owner=request.user)

    # Pagination
    page_number = request.GET.get("page")
    paginator = Paginator(projects, 10)  # Show 10 projects per page.
    page_obj = paginator.get_page(page_number)
    return render(request, "projects/index.html", {"page_obj": page_obj})


@login_required
def create(request):
    """
    Create a new project.

    :param request: The HTTP request object containing project data.
    :return: HttpResponseRedirect to project detail template on successful creation.
    :return: Rendered create template with form on GET or validation errors.
    """
    # On POST request create new project
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)

        # Validate form data
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
            return render(request, "projects/create.html", {"form": form})
    else:
        # For GET requests, show empty form
        form = ProjectForm()
        return render(request, "projects/create.html", {"form": form})


@login_required
def update(request, pk):
    """
    Update an existing project.

    :param request: The HTTP request object containing updated project data.
    :param pk (int): Primary key of the project to update.
    :raises Http404: If the project doesn't exist or user isn't the owner.
    :return: HttpResponseRedirect to project detail template on successful update.
    :return: Rendered update template with form on GET or validation errors.
    """
    # Get the project and verify ownership
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    # On POST request update project data
    if request.method == "POST":
        # Initialize form with POST data, FILES and existing project instance
        form = ProjectForm(request.POST, request.FILES, instance=project)

        # Check the form data is valid
        if form.is_valid():
            # save the project data into database
            project = form.save(commit=False)
            project.is_public = form.cleaned_data["is_public"] == "True"
            project.save()

            # Update project's technologies
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
            return render(
                request, "projects/update.html", {"form": form, "project": project}
            )
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


@csrf_exempt
@login_required
def delete(request, pk):
    """
    Delete an existing project.

    :param request: The HTTP request object.
    :param pk (int): Primary key of the project to delete.
    :raises Http404: If the project doesn't exist or user isn't the owner.
    :return: HttpResponse with status 204 on successful deletion.
    :return: JsonResponse with error message on non-DELETE requests.
    """
    if request.method != "DELETE":
        return JsonResponse({"error": "DELETE request required."}, status=400)

    project = get_object_or_404(Project, pk=pk, owner=request.user)
    project.delete()
    return HttpResponse(status=204)


@login_required
def detail(request, pk):
    """
    Display the details of a specific project.

    :param request: The HTTP request object.
    :param pk (int): Primary key of the project to display.
    :raises Http404: If the project doesn't exist.
    :return: HttpResponse with status 403 if user can't access the project.
    :return: Rendered detail template with project data.
    """
    # Get project object
    project = get_object_or_404(Project, pk=pk)

    # Check project visibility.
    if not project.is_public and request.user != project.owner:
        return render(request, "projects/detail.html")

    # Add unique viewer if they are not the owner
    if request.user not in project.viewers.all() and request.user != project.owner:
        project.viewers.add(request.user)

    return render(request, "projects/detail.html", {"project": project})


@csrf_exempt
@login_required
def reviews(request, pk):
    """
    Add a review to a specific project.

    :param request: The HTTP request object containing review content.
    :param pk (int): Primary key of the project to review.
    :raises Http404: If the project doesn't exist.
    :return: JsonResponse with success message and status 201 on successful creation.
    :return: JsonResponse with error message on failure or non-POST requests.
    """
    # Allow only POST request
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
    """
    Toggle star status for a specific project.

    :param request: The HTTP request object.
    :param pk (int): Primary key of the project to star/unstar.
    :raises Http404: If the project doesn't exist.
    :return: JsonResponse with updated star status and count.
    :return: JsonResponse with error message on non-POST requests.
    """
    # Allow only POST request
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
    """
    Change the visibility status of a project.

    :param request: The HTTP request object containing visibility data.
    :param pk (int): Primary key of the project to update.
    :raises Http404: If the project doesn't exist.
    :return: JsonResponse with success message and updated visibility status.
    :return: JsonResponse with error message if user isn't the owner or on non-PUT requests.
    """
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

    # access request body data
    data = json.loads(request.body)

    # Change visibility
    project.is_public = data.get("visibility") == "public"

    # Save changes
    project.save()

    return JsonResponse(
        {"message": "visibility changes successfully.", "is_public": project.is_public},
        status=200,
    )
