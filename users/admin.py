from django.contrib import admin

# Register your models here.

from . import models

class FriendRequestAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('sender', 'receiver', 'status', 'created_on', 'updated_on')
    # Optional: Add filters by status and date
    list_filter = ('status', 'created_on')
    # Optional: Enable searching by sender and receiver
    search_fields = ('sender__email', 'receiver__email')

admin.site.register(models.FriendRequest, FriendRequestAdmin)
admin.site.register(models.UserLog)
