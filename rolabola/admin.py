from django.contrib import admin

# Register your models here.
from rolabola.models import *

class GroupAdmin(admin.ModelAdmin):
    pass
admin.site.register(Group, GroupAdmin)
