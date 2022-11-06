from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveSmallIntegerField, SlugField, TextField,
                              UniqueConstraint)
from django.db.models.functions import Length

CharField.register_lookup(Length)

User = get_user_model()


class Tag(Model):
    """Тег для рецепта."""
    name = CharField(
        'Название тэга',
        blank=False,
        max_length=settings.TAG_NAME_LENGTH,
        help_text='Название тэга',
        unique=True,
    )
    color = CharField(
        'Цвет тега',
        max_length=6,
        unique=True,
    )
    slug = SlugField(
        unique=True,
        max_length=settings.TAG_NAME_LENGTH,
        verbose_name='Метка URL',
        blank=False,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(Model):
    """Ингридиенты для рецептов."""
    name = CharField(
        verbose_name='Ингридиент',
        max_length=settings.INGRIDIENT_NAME_LENGTH,
    )
    measurement_unit = CharField(
        verbose_name='Еденица измерения',
        max_length=settings.MEASURMENT_COUNT_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ('name', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_for_ingridient'
            ),
        )

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Recipe(Model):
    """Модель рецептов."""
    name = CharField(
        verbose_name='Блюдо',
        max_length=settings.RECIPE_NAME_LENGTH,
    )
    author = ForeignKey(
        verbose_name='Автор',
        related_name='recipes',
        to=User,
        on_delete=CASCADE,
    )
    favorite = ManyToManyField(
        verbose_name='Избранные рецепты',
        related_name='favorites',
        to=User,
    )
    tags = ManyToManyField(
        verbose_name='Тег',
        related_name='recipes',
        to='Tag',
    )
    ingredients = ManyToManyField(
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
        to=Ingredient,
        through='AmountIngredient',
    )
    cart = ManyToManyField(
        verbose_name='Список покупок',
        related_name='carts',
        to=User,
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    image = ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
    )
    text = TextField(
        verbose_name='Описание',
    )
    cooking_time = PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        default=0,
        validators=(
            MinValueValidator(
                1
            ),
            MaxValueValidator(
                600
            )
        ),
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', )
        constraints = (
            UniqueConstraint(
                fields=('name', 'author', ),
                name='unique_for_author'
            ),
        )

    def __str__(self) -> str:
        return f'{self.name}. Автор: {self.author.username}'


class AmountIngredient(Model):
    """Ингридиенты в блюде"""
    recipe = ForeignKey(
        verbose_name='В каких рецептах',
        related_name='ingredient',
        to=Recipe,
        on_delete=CASCADE,
    )
    ingredients = ForeignKey(
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        to=Ingredient,
        on_delete=CASCADE,
    )
    amount = PositiveSmallIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(
                1
            ),
            MaxValueValidator(
                10000
            ),
        ),
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Количество ингридиентов'
        ordering = ('recipe', )
        constraints = (
            UniqueConstraint(
                fields=('recipe', 'ingredients', ),
                name='\n%(app_label)s_%(class)s ingredient alredy added\n',
            ),
        )

    def __str__(self) -> str:
        return f'{self.amount} {self.ingredients}'
