from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Домашние задания — администрирование"
admin.site.site_title = "Админка"
admin.site.index_title = "Панель управления"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("", include("homework.urls")),
]