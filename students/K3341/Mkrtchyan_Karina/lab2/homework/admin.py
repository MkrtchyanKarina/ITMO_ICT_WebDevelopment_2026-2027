from django.contrib import admin
from .models import Subject, Homework, Penalty, Submission, Grade


class PenaltyInline(admin.TabularInline):
    model = Penalty
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("subject", "teacher", "issued_at", "deadline")
    list_filter = ("subject", "teacher", "deadline")
    search_fields = ("text",)
    inlines = [PenaltyInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("homework", "student", "submitted_at")
    list_filter = ("homework__subject", "homework")
    search_fields = ("student__username",)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("submission", "value", "graded_at")
    list_filter = ("value",)