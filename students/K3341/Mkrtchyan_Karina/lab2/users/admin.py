from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "school_class")
    search_fields = ("user__username",)
    list_filter = ("school_class",)