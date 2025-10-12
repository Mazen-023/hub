from django.db import models

from accounts.models import User

# Technology model related to a project
class Technology(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

# Project created by a user
class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    overview = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    image = models.ImageField(blank=True, upload_to="media")
    objectives = models.TextField(blank=True)
    key_learning = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    technologies = models.ManyToManyField(
        Technology, related_name="projects", blank=True
    )
    viewers = models.ManyToManyField(
        User, related_name="viewed_projects", blank=True, editable=False
    )
    stars = models.ManyToManyField(User, related_name="starred_projects", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"project: {self.title}, created by {self.owner.username}."


# User adds a review on a project
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewed")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="reviews"
    )
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} on {self.project.title}"
