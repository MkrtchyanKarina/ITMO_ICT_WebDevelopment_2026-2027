from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Homework, Submission
from .forms import SubmissionForm
from django.contrib.auth.models import User
from .models import Grade

def homework_list(request):
    homeworks = Homework.objects.select_related("subject", "teacher").all()
    return render(request, "homework/homework_list.html", {"homeworks": homeworks})


@login_required
def homework_detail(request, pk):
    hw = get_object_or_404(Homework, pk=pk)
    # уже сдавал?
    existing = Submission.objects.filter(homework=hw, student=request.user).first()

    if request.method == "POST":
        form = SubmissionForm(request.POST, instance=existing)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.homework = hw
            submission.student = request.user
            submission.save()
            return redirect("homework:detail", pk=hw.pk)
    else:
        form = SubmissionForm(instance=existing)

    return render(request, "homework/homework_detail.html", {
        "hw": hw,
        "form": form,
        "existing": existing,
    })


@login_required
def grade_table(request):
    profile = getattr(request.user, "profile", None)
    school_class = profile.school_class if profile and profile.school_class else request.GET.get("class")

    students = User.objects.filter(
        is_staff=False, profile__school_class=school_class
    ).order_by("username")

    homeworks = Homework.objects.select_related("subject").order_by("subject__name", "deadline")

    grades = {}
    for g in Grade.objects.select_related("submission__student", "submission__homework"):
        grades[(g.submission.student_id, g.submission.homework_id)] = g.value

    rows = []
    for student in students:
        row = {"student": student, "cells": []}
        for hw in homeworks:
            row["cells"].append(grades.get((student.id, hw.id), "—"))
        rows.append(row)

    return render(request, "homework/grade_table.html", {
        "school_class": school_class,
        "homeworks": homeworks,
        "rows": rows,
    })