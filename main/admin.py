from django.contrib import admin
from .models import Service, News, Contact, SiteSettings, Order, SupportChat, ServiceOrder

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title',)
    list_filter = ('date',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('title', 'user__username')

@admin.register(SupportChat)
class SupportChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'sender', 'created_at', 'is_admin')
    list_filter = ('is_admin', 'created_at')
    search_fields = ('user__username', 'sender__username', 'message')

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ('service', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'service__title', 'description')