from django.contrib import admin
from .models import Robots, Email, Clients, EmailService


class RobotsDisplay(admin.ModelAdmin):
    list_display = ('name', 'info', 'date')
    list_display_links = ('name', )
    search_fields = ('name', )


class EmailServiceDisplay(admin.ModelAdmin):
    list_display = ('service_name',)


class EmailDisplay(admin.ModelAdmin):
    list_display = ('email', )
    list_display_links = ('email',)
    search_fields = ('email',)


class ClientDisplay(admin.ModelAdmin):
    list_display = ('client_name', 'client_id', 'user_key', 'org', 'folder', 'tenant')
    list_display_links = ('client_name', 'client_id', 'user_key', 'org', 'folder', 'tenant')
    search_fields = ('client_name', 'client_id', 'user_key', 'org', 'folder', 'tenant')


admin.site.register(Robots, RobotsDisplay)
admin.site.register(Email, EmailDisplay)
admin.site.register(Clients, ClientDisplay)
admin.site.register(EmailService, EmailServiceDisplay)
