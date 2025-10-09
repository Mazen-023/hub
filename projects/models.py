from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


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

    def __str__(self):
        return f"{self.username} have {self.followers.count()} Followers"


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
    # Track the users who see this project
    viewers = models.ManyToManyField(User, related_name="viewed_projects", blank=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"project: {self.title}, created by {self.owner.username}."


class Tech(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tech")
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.project.owner.username} have {self.name} skill."
