

from django.contrib import admin
from .models import Event, EventRegistration,BarcodeScan

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location', 'created_by', 'view_registered_users')

    def view_registered_users(self, obj):
        return f'<a href="/admin/events/event/{obj.id}/registered_users/">View Registered Users</a>'
    view_registered_users.allow_tags = True
    view_registered_users.short_description = 'Registered Users'

admin.site.register(Event, EventAdmin)
admin.site.register(EventRegistration)

admin.site.register(BarcodeScan)


