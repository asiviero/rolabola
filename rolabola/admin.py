from django.contrib import admin

# Register your models here.
from rolabola.models import *

class GroupAdmin(admin.ModelAdmin):
    pass
class MatchAdmin(admin.ModelAdmin):
    pass
class VenueAdmin(admin.ModelAdmin):
    pass

admin.site.register(Group, GroupAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Venue, VenueAdmin)
