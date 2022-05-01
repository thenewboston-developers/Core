from django.contrib import admin

from .models import Config


class ConfigAdmin(admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# TODO(dmu) LOW: For some reason @admin.site.register(Setting) raises TypeError
admin.site.register(Config, ConfigAdmin)
