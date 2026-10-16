from django.urls import path
from . import views

app_name = "homework"

urlpatterns = [
    path("", views.HomeworkListView.as_view(), name="list"),
    path("grades/", views.grade_table, name="grade_table"),
    path("<int:pk>/", views.homework_detail, name="detail"),
]