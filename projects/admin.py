from django.contrib import admin


from .models import User, Project, Tech, Review

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Tech)
admin.site.register(Review)
