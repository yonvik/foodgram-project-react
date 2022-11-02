from django.conf import settings
from drf_extra_fields.fields import Base64ImageField
from django.db.models import F
from rest_framework import serializers

from recipes.validators import check_value_validate
from recipes.utils import recipe_amount_ingredients_set
from recipes.models import Ingredient, Recipe, Tag, AmountIngredient
from users.models import User
from users.validators import username_validator


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для использования с моделью User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj):
        """Проверка подписки пользователей."""

        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.subscribe.filter(id=obj.id).exists()

    def create(self, validated_data):
        """ Создаёт нового пользователя с запрошенными полями."""

        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        """Проверяет введённый юзернейм."""

        return username_validator(value)


class UserSubscribeSerializer(UserSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь."""

    recipes = ShortRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        """ Показывает общее количество рецептов у каждого автора."""

        return obj.recipes.count()


class TokenSerializer(serializers.Serializer):
    """Сериалазер без модели, для полей email и password."""

    email = serializers.EmailField(
        max_length=settings.EMAIL_LENGTH, required=True)
    password = serializers.CharField(
        max_length=settings.PASSWORD_LENGTH, required=True)


class TagSerializer(serializers.ModelSerializer):
    """Сериалазер для модели Tag."""

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',
        )
        

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart',
        )

    def get_ingredients(self, obj):
        """Получает список ингридиентов для рецепта."""

        ingredients = obj.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        """Проверка - находится ли рецепт в избранном."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка - находится ли рецепт в списке  покупок."""

        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.carts.filter(id=obj.id).exists()
        
    def to_internal_value(self, data):
        new_data = super().to_internal_value(data)
        new_data['ingredients'] = data['ingredients']
        return new_data

    def create_amount_ingredients(self, ingredients, recipe):
        """Обновляет ингридиенты в рецепте."""
        new_ingredients = [
            AmountIngredient(
                recipe=recipe,
                ingredients=ingredient['ingredient'],
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        AmountIngredient.objects.bulk_create(new_ingredients)

    def validate(self, data):
        """Проверка вводных данных при создании/редактировании рецепта."""

        name = str(self.initial_data.get('name')).strip()
        tags = self.initial_data.get('tags')
        ingredients = data['ingredients']
        values_as_list = (tags, ingredients)

        for value in values_as_list:
            if not isinstance(value, list):
                raise serializers.ValidationError(
                    f'"{value}" должен быть в формате "[]"'
                )

        for tag in tags:
            check_value_validate(tag, Tag)

        valid_ingredients = []
        for ing in ingredients:
            ing_id = ing.get('id')
            ingredient = check_value_validate(ing_id, Ingredient)

            amount = ing.get('amount')
            check_value_validate(amount)

            valid_ingredients.append(
                {'ingredient': ingredient, 'amount': amount}
            )

        data['name'] = name.capitalize()
        data['tags'] = tags
        data['ingredients'] = valid_ingredients
        data['author'] = self.context.get('request').user
        return data

    def create(self, validated_data):
        """Создаёт рецепт."""

        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        recipe_amount_ingredients_set(recipe, ingredients)
        return recipe

    def update(self, obj, validated_data):
        """Обновляет рецепт."""

        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            obj.ingredients.clear()
            self.create_amount_ingredients(ingredients, obj)
        if 'tags' in validated_data:
            tags = validated_data.pop('tags')
            obj.tags.set(tags)
        return super().update(obj, validated_data)
