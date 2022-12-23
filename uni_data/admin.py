from django.contrib import admin

from uni_data.models import Course, Previous, Professor

# Register your models here.
admin.site.register(Course)
admin.site.register(Previous)
admin.site.register(Professor)
