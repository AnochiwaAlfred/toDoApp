from django.contrib import admin
from users.models import *
from django.contrib.auth.admin import UserAdmin

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    search_fields = ["email__startswith", "username__startswith"]
    list_display = [
        "id",
        "username",
        "email",
        "is_staff",
        "is_superuser",
    ]
    list_filter = ["is_staff", "is_superuser"]
    list_display_links = ["username", "email"]
    ordering = ["id"]
    filter_horizontal = []
    fieldsets = [
        (None, {"fields": ["username", "email", "password"]}),
        # ("Personal Info", {"fields": ["firstName", "lastName", "phone"]}),
        ("Permissions", {"fields": ["is_staff", "is_superuser"]}),
    ]


@admin.register(Client)
class ClientAdmin(UserAdmin):
    search_fields = ["email__startswith", "username__startswith"]
    list_display = [
        "id", 
        "username", 
        "email", 
        ]
    list_display_links = ["username", "email"]
    list_filter = []
    ordering = ["id"]
    filter_horizontal = []
    fieldsets = [
        (None, {"fields": ["username", "email", "password"]}),
        (
            "Personal Info",
            {"fields": ["phone", "image"]},
        ),
        ("Permissions", {"fields": []}),
    ]
