from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "projects/index.html")


def add(request):
    return render(request, "projects/add.html")


def project_detial(request, pk):
    return render(request, "projects/detail.html")
