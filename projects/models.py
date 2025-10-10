from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


# User entity
class User(AbstractUser):
    photo = models.ImageField(blank=True, upload_to="media")
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    def serializer(self):
        return {
            "id": self.id,
            "username": self.username,
            "photo": self.photo,
            "followers": self.followers.count(),
            "following": self.following.count(),
        }

    def is_valid_follower(self):
        return not self.following.filter(pk=self.pk).exists()


# Project created by a user
class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    overview = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    image = models.ImageField(blank=True, upload_to="media")
    objectives = models.TextField(blank=True)
    key_learning = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    viewers = models.ManyToManyField(
        User, related_name="viewed_projects", blank=True, editable=False
    )
    stars = models.ManyToManyField(User, related_name="starred_projects", blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"project: {self.title}, created by {self.owner.username}."


# Technolgoies related to a project
class Tech(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tech")
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project.owner.username} have {self.name} skill."


# User adds a review on a project
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_reviews"
    )
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user.username} on {self.project.title}"
