from django.core.validators import RegexValidator
from recipes.models import AmountIngredient
from rest_framework.serializers import ValidationError


def check_value_validate(value, klass=None):
    """Проверяет корректность переданного значения."""
    if not str(value).isdecimal():
        raise ValidationError(
            f'{value} должно содержать цифру'
        )
    if klass:
        obj = klass.objects.filter(id=value)
        if not obj:
            raise ValidationError(
                f'{value} не существует'
            )
        return obj[0]


def hex_color_validator(value):
    """Валидатор для цвета, типа HEX."""
    RegexValidator(
        r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
        message="Может содержать только буквы и цыфры, "
        "начинаться с '#' и быть длинной 6 или 3 символа, после '#'",
        code='Переданый цвет не типа HEX.'
    )(value=value)


def recipe_amount_ingredients_set(recipe, ingredients):
    """Записывает ингредиенты вложенные в рецепт."""
    for ingredient in ingredients:
        AmountIngredient.objects.get_or_create(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount']
        )
