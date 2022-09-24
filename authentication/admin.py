from django.contrib import admin
from authentication.models import SSOut, MyUser


admin.site.register(MyUser)
admin.site.register(SSOut)
