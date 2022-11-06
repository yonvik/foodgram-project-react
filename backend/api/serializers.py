from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import AmountIngredient, Ingredient, Recipe, Tag
from rest_framework import serializers
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
            'id',
            'name',
            'color',
            'slug',
        )
        

class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода ингридиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField() 
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            'cooking_time'
        )

    def get_ingredients(self, obj): 
        """Получает список ингридиентов для рецепта.""" 

        ingredients = obj.ingredients.values( 
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount') 
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

        
class RecipesCreateSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания и редактирования рецептов."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    ingredients = serializers.ListField()
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def create_amount_ingredients(self, ingredients, recipe):
        """Обновляет ингридиенты в рецепте."""
        
        create_ingredient = [
            AmountIngredient(
                recipe=recipe,
                ingredients=get_object_or_404(Ingredient, pk=ingredient["id"]),
                amount=ingredient['amount']
            )
            for ingredient in ingredients]
        AmountIngredient.objects.bulk_create(create_ingredient)

    
    def create(self, validated_data):
        """Создаёт рецепт."""

        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_amount_ingredients(ingredients, recipe)
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

    def validate(self, data):
        ingredients = data['ingredients']
        unique_ings = []
        for ingredient in ingredients:
            name = ingredient['id']
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError(
                    f'Не корректное количество для {name}'
                )
            if name not in unique_ings:
                unique_ings.append(name)
            else:
                raise serializers.ValidationError('Ингредиенты повторяются!')
        return data

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }).data
