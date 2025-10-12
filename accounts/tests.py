from django.test import TestCase

from .models import User


class UserTestCase(TestCase):
    def setUp(self):
        # Create user
        foo = User.objects.create(username="foo")
        bar = User.objects.create(username="bar")
        baz = User.objects.create(username="baz")

        # Set up followers
        foo.following.add(foo)
        bar.following.add(baz)
        baz.following.add(bar)

    def test_valid_follower(self):
        """User is NOT following themselves, should be valid."""
        user = User.objects.get(username="baz")
        self.assertTrue(user.is_valid_follower())

    def test_invalid_follower(self):
        """User is following themselves, should be invalid."""
        user = User.objects.get(username="foo")
        self.assertFalse(user.is_valid_follower())
