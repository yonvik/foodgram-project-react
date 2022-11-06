import csv
import os.path

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка списка ингредиентов'

    def handle(self, *args, **kwargs):
        file_name = 'data/ingredients.csv'
        file_path = os.path.abspath(
            os.path.join(settings.BASE_DIR, file_name)
        )
        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    for row in reader:
                        Ingredient.objects.update_or_create(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                    self.stdout.write(self.style.SUCCESS(
                        'Ингредиенты успешно добавлены'
                    ))
                except Exception:
                    self.stdout.write(self.style.WARNING('Ошибка'))
        except IOError:
            self.stdout.write(
                self.style.WARNING(
                    f'проверьте наличие файла {file_name} в {file_path}'
                )
            )
