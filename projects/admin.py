from django.contrib import admin


from .models import User, Project, Technology, Review

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Technology)
admin.site.register(Review)
