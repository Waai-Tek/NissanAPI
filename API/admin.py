from django.contrib import admin
from .models import UserProfile, QuickLinks, ActiveObjects, Devices, DeviceAnalytics
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.
admin.site.unregister(User)  # Necessary

admin.site.register(QuickLinks)
admin.site.register(ActiveObjects)
admin.site.register(Devices)
admin.site.register(DeviceAnalytics)


class UserProfileInline(admin.TabularInline):
    model = UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
