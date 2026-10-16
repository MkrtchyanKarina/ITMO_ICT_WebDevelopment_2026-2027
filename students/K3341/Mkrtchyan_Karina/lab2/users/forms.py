from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(label="Логин", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput)
    school_class = forms.CharField(
        label="Класс",
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            "list": "class-list",  # список подсказок существующих классов
            "autocomplete": "off",  # не подставляем значения в браузере автоматически
            "placeholder": "Например, 10А",  # подсказка внутри поля
        }),
    )

    def clean_username(self):
        from django.contrib.auth.models import User
        username = self.cleaned_data["username"]  # берем поле из словаря cleaned_data, которое уже прошло валидацию встроенным cleaned()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Такой логин уже занят.")
        return username

    def clean_password2(self):  # проверяем пароли, так как они не прошли валидацию еще, получаем их через .get()
        p1 = self.cleaned_data.get("password")
        p2 = self.cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        return p2