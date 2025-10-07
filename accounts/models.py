from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    def serializer(self):
        return {
            "id": self.id,
            "username": self.username,
            "followers": self.followers.count(),
            "following": self.following.count(),
        }

    def is_valid_follower(self):
        return not self.following.filter(pk=self.pk).exists()

    def __str__(self):
        return f"{self.username} have {self.followers.count()} Followers"
