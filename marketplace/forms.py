from django import forms
from .models import BusinessRequest, Offer

class RequestForm(forms.ModelForm):
    class Meta:
        model = BusinessRequest
        fields = ("category", "title", "description", "quantity", "budget_min", "budget_max", "city", "deadline")
        labels = {"category":"Категория / Категория", "title":"Что вам нужно? / Сизге эмне керек?", "description":"Описание и требования / Сүрөттөмө жана талаптар", "quantity":"Количество / Саны", "budget_min":"Бюджет от, сом / Бюджеттен, сом", "budget_max":"Бюджет до, сом / Бюджетке чейин, сом", "city":"Город / Шаар", "deadline":"Желаемый срок / Каалаган мөөнөт"}
        widgets = {"description":forms.Textarea(attrs={"rows":5}), "deadline":forms.DateInput(attrs={"type":"date"})}
    def clean(self):
        data = super().clean()
        low, high = data.get("budget_min"), data.get("budget_max")
        if low is not None and high is not None and low > high:
            self.add_error("budget_max", "Максимальный бюджет должен быть не меньше минимального.")
        return data

class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ("price", "delivery_days", "details")
        labels = {"price":"Цена, сом / Баасы, сом", "delivery_days":"Срок выполнения, дней / Аткаруу мөөнөтү, күн", "details":"Условия и комментарий / Шарттар жана комментарий"}
        widgets = {"details":forms.Textarea(attrs={"rows":3})}
