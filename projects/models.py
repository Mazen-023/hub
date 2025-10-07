from django.db import models

from accounts.models import User


# Create your models here.
class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    overview = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    erd_image = models.ImageField(blank=True, upload_to="media")
    objectives = models.TextField(blank=True)
    key_learning = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    views = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"project: {self.title}, created by {self.owner.username}."


class Tech(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tech")
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project.owner.username} have {self.name} skill."
