from django.contrib import admin


from .models import Project, Tech

# Register your models here.
admin.site.register(Project)
admin.site.register(Tech)