from django.conf import settings
from django.db import models
from django.utils import timezone


class Subject(models.Model):
    """ Таблица Subject для хранения названий и описаний предметов """
    name = models.CharField("Название", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:  # метаданные для изменения поведения модели
        verbose_name = "Предмет"  # удобное название поля для отображения на сайте
        verbose_name_plural = "Предметы"
        ordering = ["name"]  # сортировка по названию

    def __str__(self):
        return self.name


class Homework(models.Model):
    """ Таблица Homework для хранения информации о домашних заданиях """
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="homeworks",  # обратное имя для получения subject.homeworks - дз по данному предмету
        verbose_name="Предмет",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,  # оставляем пустую строку, если значение на записано
        related_name="created_homeworks",  # обратное имя для получения user.created_homeworks - дз от данного учителя
        limit_choices_to={"is_staff": True},   # только учителя/админы
        verbose_name="Преподаватель",
    )
    issued_at = models.DateField("Дата выдачи", default=timezone.now)
    deadline = models.DateField("Срок выполнения")
    text = models.TextField("Текст задания")

    class Meta:
        verbose_name = "Домашнее задание"
        verbose_name_plural = "Домашние задания"
        ordering = ["-issued_at", "deadline"]  # ортировка сначала по дате выдачи по убыванию, затем по дедлайну по возрастанию

    def __str__(self):
        return f"{self.subject.name}: {self.text[:40]}"

    def is_overdue(self):
        return timezone.now().date() > self.deadline


class Penalty(models.Model):
    """ Таблица Penalty - штрафы по заданиям """
    homework = models.ForeignKey(
        Homework,
        on_delete=models.CASCADE,
        related_name="penalties",  # обратное имя для получения homework.penalties - штрафов по данному дз
        verbose_name="Домашнее задание",
    )
    description = models.CharField("Описание штрафа", max_length=255)
    points = models.PositiveSmallIntegerField("Размер штрафа (в баллах)", default=1)

    class Meta:
        verbose_name = "Штраф"
        verbose_name_plural = "Штрафы"

    def __str__(self):
        return f"{self.homework} — −{self.points} ({self.description})"


class Submission(models.Model):
    """Сдача домашнего задания учеником."""
    homework = models.ForeignKey(  # связь с таблицами дз и учеников по внешним ключам
        Homework,
        on_delete=models.CASCADE,
        related_name="submissions",  # получение отправок дз - homework.submissions
        verbose_name="Домашнее задание",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",  # получение решений ученика - student.submissions
        limit_choices_to={"is_staff": False},   # только ученики
        verbose_name="Ученик",
    )
    text = models.TextField("Текст ответа")
    submitted_at = models.DateTimeField("Дата сдачи", auto_now_add=True)

    class Meta:
        verbose_name = "Сдача задания"
        verbose_name_plural = "Сдачи заданий"
        unique_together = ("homework", "student")  # получение последней отправки дз учеником
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.student} -> {self.homework}"


class Grade(models.Model):
    """Оценка, выставленная учителем за сдачу."""
    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name="grade",  # submission.grade - получение оценки
        verbose_name="Сдача",
    )
    value = models.PositiveSmallIntegerField("Оценка")
    comment = models.TextField("Комментарий учителя", blank=True)
    graded_at = models.DateTimeField("Дата выставления", auto_now_add=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        ordering = ["-graded_at"]

    def __str__(self):
        return f"{self.submission.student} — {self.value}"