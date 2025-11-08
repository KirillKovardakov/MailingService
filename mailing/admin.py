from django.contrib import admin
from .models import Mailing, Profile, Recipient, Message


@admin.register(Profile)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'is_blocked')
    list_filter = ('user', 'role')
    search_fields = ('user', 'role',)


@admin.register(Recipient)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'comment', 'owner', 'created_at', 'updated_at')
    list_filter = ('email', 'full_name', 'comment', 'owner')
    search_fields = ('email', 'full_name', 'comment', 'owner',)


@admin.register(Message)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'body', 'owner', 'created_at', 'updated_at')
    list_filter = ('subject', 'body', 'owner')
    search_fields = ('subject', 'body', 'owner',)


@admin.register(Mailing)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_at', 'end_at', 'status', 'message', 'owner', 'created_at', 'updated_at')
    list_filter = ('start_at', 'end_at', 'status', 'message', 'owner')
    search_fields = ('start_at', 'end_at', 'status', 'message', 'owner',)
