from django import forms
from .models import BusinessRequest, Offer, SupplierListing


class PrivacyConsentMixin:
    privacy_consent = forms.BooleanField(
        required=True,
        label="Я согласен(на) на обработку персональных данных и принимаю политику конфиденциальности.",
        error_messages={
            "required": "Для продолжения необходимо дать согласие на обработку персональных данных."
        },
    )


class RequestForm(forms.ModelForm):
    privacy_consent = forms.BooleanField(
        required=True,
        label=PrivacyConsentMixin.privacy_consent.label,
        error_messages=PrivacyConsentMixin.privacy_consent.error_messages,
    )
    class Meta:
        model = BusinessRequest
        fields = (
            "category", "title", "description", "quantity",
            "budget_min", "budget_max", "city", "deadline",
        )
        labels = {
            "category": "Категория",
            "title": "Что вам нужно?",
            "description": "Описание и требования",
            "quantity": "Количество",
            "budget_min": "Бюджет от, сом",
            "budget_max": "Бюджет до, сом",
            "city": "Город",
            "deadline": "Желаемый срок",
        }
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 5, "maxlength": 5000}),
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"maxlength": 200}),
            "city": forms.TextInput(attrs={"maxlength": 100}),
        }

    def clean(self):
        data = super().clean()
        low, high = data.get("budget_min"), data.get("budget_max")
        if low is not None and high is not None and low > high:
            self.add_error(
                "budget_max",
                "Максимальный бюджет не может быть меньше минимального.",
            )
        return data


class OfferForm(forms.ModelForm):
    privacy_consent = forms.BooleanField(
        required=True,
        label=PrivacyConsentMixin.privacy_consent.label,
        error_messages=PrivacyConsentMixin.privacy_consent.error_messages,
    )
    class Meta:
        model = Offer
        fields = ("price", "delivery_days", "details")
        labels = {
            "price": "Цена, сом",
            "delivery_days": "Срок выполнения, дней",
            "details": "Условия и комментарий",
        }
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3, "maxlength": 3000}),
        }


class SupplierListingForm(forms.ModelForm):
    privacy_consent = forms.BooleanField(
        required=True,
        label=(
            "Я согласен(на) на обработку персональных данных "
            "и принимаю политику конфиденциальности."
        ),
    )

    class Meta:
        model = SupplierListing
        fields = (
            "category", "title", "description",
            "price", "quantity", "city", "deadline",
        )
        labels = {
            "category": "Категория",
            "title": "Название товара или услуги",
            "description": "Описание",
            "price": "Цена, сом",
            "quantity": "Количество или объём",
            "city": "Город",
            "deadline": "\u0421\u0440\u043e\u043a \u043f\u043e\u0434\u0430\u0447\u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0435\u043d\u0438\u0439",
            "image_url": "Ссылка на фотографию (необязательно)",
        }
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 5, "maxlength": 5000}
            ),
            "title": forms.TextInput(attrs={"maxlength": 180}),
            "quantity": forms.TextInput(attrs={"maxlength": 120}),
            "city": forms.TextInput(attrs={"maxlength": 80}),
            "deadline": forms.DateInput(
                format="%Y-%m-%d",
                attrs={
                    "type": "date",
                    "placeholder": "mm/dd/yyyy",
                },
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = (
            self.fields["category"].queryset.filter(is_active=True)
        )


class OrderCreateForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=1000000,
        initial=1,
        label="Количество",
    )
    buyer_note = forms.CharField(
        required=False,
        max_length=2000,
        label="Комментарий к заказу",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Укажите пожелания к заказу",
        }),
    )
