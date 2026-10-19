from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "company_name", "city", "phone", "password1", "password2")
        labels = {
            "username": "Логин / Колдонуучу аты", "first_name": "Имя / Аты", "last_name": "Фамилия / Фамилиясы",
            "email": "Email", "role": "Я регистрируюсь как / Мен катталам", "company_name": "Компания / Компания",
            "city": "Город / Шаар", "phone": "Телефон / Телефон",
        }
        widgets = {"role": forms.Select(), "company_name": forms.TextInput(attrs={"placeholder":"Например, ОсОО Альфа"})}

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "role", "company_name", "city", "phone", "about")
        labels = {"first_name":"Имя / Аты", "last_name":"Фамилия / Фамилиясы", "email":"Email", "role":"Роль / Ролу", "company_name":"Компания / Компания", "city":"Город / Шаар", "phone":"Телефон / Телефон", "about":"О компании / Компания жөнүндө"}
