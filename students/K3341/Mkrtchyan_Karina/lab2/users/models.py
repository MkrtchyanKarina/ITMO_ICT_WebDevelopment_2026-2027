from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """ Таблица Profile для хранения информации о пользователях """
    user = models.OneToOneField(
        User,  # используем стандартную модель пользователя со всеми полями и расширяем ее, добавляя класс для учеников
        on_delete=models.CASCADE,  # удаление строк в зависимых таблицах при удалении пользователя
        related_name="profile",  # обратное имя для получения user.profile (вместо user.profile_set - по-умолчанию)
        verbose_name="Пользователь",  # удобное название поля для отображения на сайте
    )
    school_class = models.CharField(
        "Класс",
        max_length=10,
        blank=True,  # оставляем пустую строку, если значение на записано
    )

    class Meta:
        verbose_name = "Профиль"  # удобное название модели для отображения на сайте
        verbose_name_plural = "Профили"

    def __str__(self):
        # строковое представление объекта данной модели
        return f"{self.user.username} ({self.school_class or '—'})"