from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email", "role",
            "company_name", "city", "phone", "password1", "password2",
        )
        labels = {
            "username": "\u041b\u043e\u0433\u0438\u043d",
            "first_name": "\u0418\u043c\u044f",
            "last_name": "\u0424\u0430\u043c\u0438\u043b\u0438\u044f",
            "role": "\u041a\u0442\u043e \u0432\u044b",
            "company_name": "\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f",
            "city": "\u0413\u043e\u0440\u043e\u0434",
            "phone": "\u0422\u0435\u043b\u0435\u0444\u043e\u043d",
        }
        widgets = {
            "role": forms.Select(),
            "company_name": forms.TextInput(attrs={
                "placeholder": "\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438"
            }),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "role",
            "company_name", "company_registration_number",
            "city", "phone", "about",
        )
        labels = {
            "first_name": "\u0418\u043c\u044f",
            "last_name": "\u0424\u0430\u043c\u0438\u043b\u0438\u044f",
            "email": "Email",
            "role": "\u0420\u043e\u043b\u044c",
            "company_registration_number": "Регистрационный номер компании",
            "company_name": "\u041a\u043e\u043c\u043f\u0430\u043d\u0438\u044f",
            "city": "\u0413\u043e\u0440\u043e\u0434",
            "phone": "\u0422\u0435\u043b\u0435\u0444\u043e\u043d",
            "about": "\u041e \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }
