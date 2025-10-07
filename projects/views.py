from django.shortcuts import render


from .models import Project

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
        return render(request, "projects/detail.html", {
            "message": "Project doesn't exist"
        })

    return render(request, "projects/detail.html", {
        "project": project
    })
