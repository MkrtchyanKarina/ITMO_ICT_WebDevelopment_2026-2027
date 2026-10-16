from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "school_class")
    list_editable = ("school_class",)  # смена названия класса в списке классов
    search_fields = ("user__username",)  # поиск по логину
    list_filter = ("school_class",)  # фильтр по классу