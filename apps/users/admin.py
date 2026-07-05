from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-created_at"]
    list_display = ["email", "name", "surname", "is_staff", "is_active", "created_at"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email", "name", "surname"]
    readonly_fields = ["created_at", "last_login"]
    actions = ["block_users", "unblock_users"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личная информация", {"fields": ("name", "surname", "avatar", "about", "phone", "github_url")}),
        ("Избранное", {"fields": ("favorites",)}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "surname", "password1", "password2"),
        }),
    )
    filter_horizontal = ["favorites", "groups", "user_permissions"]

    @admin.action(description="Заблокировать выбранных")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать выбранных")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)
