from django.contrib.auth.models import AbstractUser
from django.db import models

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
