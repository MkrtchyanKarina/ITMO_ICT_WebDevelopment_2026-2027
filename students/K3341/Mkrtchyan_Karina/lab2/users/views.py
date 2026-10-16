from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import Profile


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():  # проверка всех полей и вызов функций clean_username, clean_password2
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            # is_staff=False -> ученик
            Profile.objects.create(
                user=user,
                school_class=form.cleaned_data["school_class"],
            )
            login(request, user)
            return redirect("homework:list")
    else:
        form = RegisterForm()

    # подсказки уже существующих классов для datalist
    classes = (
        Profile.objects.exclude(school_class="")
        .values_list("school_class", flat=True)
        .distinct()  # берем множество значений
        .order_by("school_class")  # сортировка
    )
    return render(request, "users/register.html", {"form": form, "classes": classes})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("homework:list")
    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    return redirect("users:login")