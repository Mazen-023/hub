from django.test import TestCase

from .models import User, Project, Tech


# Create your tests here.


class ProjectTestCase(TestCase):
    def setUp(self):
        # Create user
        foo = User.objects.create(username="foo")
        bar = User.objects.create(username="bar")
        baz = User.objects.create(username="baz")

        # Set up followers
        foo.following.add(foo)
        bar.following.add(baz)
        baz.following.add(bar)

        # Create project
        project = Project.objects.create(owner=foo, title="test project 1")
        Project.objects.create(
            owner=bar,
            title="test project 2",
            description="project 2 description",
            overview="project 2 overview",
        )

        # Set up viewers
        project.viewers.add(baz)
        project.viewers.add(bar)

        # Set up stars
        project.stars.add(baz)
        project.stars.add(bar)

        # Create Tech
        Tech.objects.create(project=project, name="Django")
        Tech.objects.create(project=project, name="React")

    def test_valid_follower(self):
        """User is NOT following themselves, should be valid."""
        user = User.objects.get(username="baz")
        self.assertTrue(user.is_valid_follower())

    def test_invalid_follower(self):
        """User is following themselves, should be invalid."""
        user = User.objects.get(username="foo")
        self.assertFalse(user.is_valid_follower())

    def test_ownership(self):
        """User own a project"""
        user1 = User.objects.get(username="foo")
        user2 = User.objects.get(username="bar")
        project = Project.objects.get(title="test project 1")
        self.assertTrue(user1 == project.owner)
        self.assertFalse(user2 == project.owner)

    def test_project_detail(self):
        """Check the project detail"""
        project = Project.objects.get(title="test project 2")
        self.assertTrue(project.title == "test project 2")
        self.assertTrue(project.overview == "project 2 overview")
        self.assertTrue(project.description == "project 2 description")

    def test_tech(self):
        """Check technologies related to a project."""
        project = Project.objects.get(title="test project 2")
        techs = Tech.objects.filter(project=project)
        self.assertTrue(tech == ["Django", "React"] for tech in techs)

    def test_star(self):
        """Check if the project have stars"""
        user = User.objects.get(username="foo")
        project = Project.objects.get(owner=user)
        self.assertTrue(project.stars.count() == 2)

    def test_viewers(self):
        """Check if the project have viewers"""
        user = User.objects.get(username="foo")
        project = Project.objects.get(owner=user)
        self.assertTrue(project.viewers.count() == 2)
