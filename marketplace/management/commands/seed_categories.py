from django.core.management.base import BaseCommand
from marketplace.models import Category

class Command(BaseCommand):
    help = "Create the starter BaaTap KG categories"
    def handle(self, *args, **options):
        rows = [
            ("Полиграфия и упаковка", "Полиграфия жана таңгак", "poligrafiya-upakovka"),
            ("Вывески и наружная реклама", "Илмелер жана тышкы жарнама", "reklama-vyveski"),
            ("Сайты и цифровые услуги", "Сайттар жана санарип кызматтар", "sayt-sanarip"),
        ]
        for name_ru, name_ky, slug in rows:
            Category.objects.update_or_create(slug=slug, defaults={"name_ru": name_ru, "name_ky": name_ky, "is_active": True})
        self.stdout.write(self.style.SUCCESS("Starter categories are ready."))
