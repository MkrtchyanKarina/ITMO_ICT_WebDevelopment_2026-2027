from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView

from .models import Homework, Submission, Grade, Subject
from .forms import SubmissionForm
from users.models import Profile


def is_teacher(user):
    """Учитель/администратор — сотрудник."""
    return user.is_authenticated and user.is_staff


class HomeworkListView(ListView):
    """ Пагинация и фильтрация списка домашних заданий """
    model = Homework
    template_name = 'homework/homework_list.html'
    context_object_name = 'homeworks'
    paginate_by = 5  # по 5 заданий на страницу

    def get_queryset(self):
        queryset = super().get_queryset().select_related('subject', 'teacher')
        # subject не null, teacher может быть null, поэтому с помощью inner join получаем данные по subject, left join - teacher
        query = self.request.GET.get('q')  # извлекаем текст запроса
        subject = self.request.GET.get('subject')  # звлекаем id предмета
        if query:
            queryset = queryset.filter(text__icontains=query)  # поиск по тексту задания
        if subject:
            queryset = queryset.filter(subject_id=subject)  # поиск по предмету
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # дополнение базового контекста ListView
        context['subjects'] = Subject.objects.all()  # список существующих предметов для выпадающего списка в поиске
        # в шаблоне будет использоваться под именем subjects

        # строка запроса без page — для ссылок пагинации (поиск + фильтр)
        params = self.request.GET.copy()  # копия QueryDict с параметрами из URL для изменения
        params.pop('page', None)  # удаляем номер страницы для подстановки нового
        context['querystring'] = params.urlencode()  # превращаем в строку вида q=алгебра&subject=3 для использования в шаблоне,
        # чтобы при переходе между страницами не терялись поиск и фильтр

        # продвинутая пагинация
        page_obj = context.get('page_obj')  # берем объект текущей страницы
        paginator = context.get('paginator')
        if page_obj and paginator:
            context['page_range'] = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
            # задаем сколько страниц будет слева и справа от текущей (on_each_side) и сколько будет на концах (on_ends)
            # пример: 1 ... 4 5 6 ... 10, если номер текущей page_obj.number = 5
        # возвращаем все необходимое в шаблоне
        return context


@login_required
def homework_detail(request, pk):
    hw = get_object_or_404(Homework, pk=pk)  # получаем объект Homework по ключу
    existing = Submission.objects.filter(homework=hw, student=request.user).first()  # берем первый объект, данные фильтруются
    # с помощью настроек Meta в классе Submission

    # загрузка формы для редактирования или отправки нового решения учеником
    if request.method == "POST" and not request.user.is_staff:
        form = SubmissionForm(request.POST, instance=existing)  # если existing не None — форма работает в режиме редактирования существующей сдачи
        if form.is_valid():
            submission = form.save(commit=False)
            submission.homework = hw
            submission.student = request.user
            submission.save()
            # после успешного POST запроса делаем GET - редирект на ту же страницу,
            #  чтобы при обновлении страницы нельзя было отправить повторно форму
            return redirect("homework:detail", pk=hw.pk)

    # если existing не None, форма будет заполнена отправленными данными
    else:
        form = SubmissionForm(instance=existing)

    return render(request, "homework/homework_detail.html", {
        "hw": hw,
        "form": form,
        "existing": existing,
    })


@login_required
def grade_table(request):
    # таблица оценок всего класса — только для учителя/администратора
    if not is_teacher(request.user):
        raise PermissionDenied

    profile = getattr(request.user, "profile", None)
    # явный выбор из интерфейса (в т.ч. «Все классы» = пусто), иначе — класс учителя
    if "class" in request.GET:
        school_class = request.GET.get("class", "")
    else:
        school_class = profile.school_class if profile else ""

    students = User.objects.filter(is_staff=False)
    if school_class:
        students = students.filter(profile__school_class=school_class)  # JOIN auth_user с users_profile
    students = students.order_by("username")

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

    # список существующих классов для выпадающего списка
    classes = (
        Profile.objects.filter(user__is_staff=False)
        .exclude(school_class="")
        .values_list("school_class", flat=True)  # список значений, вместо списка кортежей
        .distinct()
        .order_by("school_class")
    )

    return render(request, "homework/grade_table.html", {
        "school_class": school_class,
        "homeworks": homeworks,
        "rows": rows,
        "classes": classes,
    })
