from django.test import TestCase

from .models import Project, Technology, Review

from accounts.models import User

class ProjectTestCase(TestCase):
    def setUp(self):
        # Create user
        foo = User.objects.create(username="foo")
        bar = User.objects.create(username="bar")
        baz = User.objects.create(username="baz")

        # Create Tech
        tech1 = Technology.objects.create(name="Django")
        tech2 = Technology.objects.create(name="React")

        # Create project
        project = Project.objects.create(owner=foo, title="test project 1")
        Project.objects.create(
            owner=bar,
            title="test project 2",
            description="project 2 description",
            overview="project 2 overview",
        )

        # Create review
        Review.objects.create(user=foo, project=project, content="test1 review")
        Review.objects.create(user=bar, project=project, content="test2 review")
        Review.objects.create(user=baz, project=project, content="test2 review")

        # Add technologies
        project.technologies.add(tech1)
        project.technologies.add(tech2)

        # Set up viewers
        project.viewers.add(baz)
        project.viewers.add(bar)

        # Set up stars
        project.stars.add(baz)
        project.stars.add(bar)


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
        techs = project.technologies.all()
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

    def test_review(self):
        """Check project's review"""
        foo = User.objects.get(username="foo")
        project = Project.objects.get(owner=foo)
        reviews = Review.objects.filter(project=project)
        self.assertTrue(reviews.count() == 3)
