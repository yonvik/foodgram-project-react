from itertools import chain
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import mixins
from rest_framework import permissions as drf_permissions
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from . import paginators, permissions, serializers
from .mixins import AddDelViewMixin
from recipes import models


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """Кастомный вьюсет Djoser."""

    pagination_class = paginators.StandardResultsSetPagination
    add_serializer = serializers.UserSubscribeSerializer

    @action(methods=settings.ACTION_METHODS, detail=True)
    def subscribe(self, request, pk):
        """Создаёт/удалет связь между пользователями."""

        return self.add_del_obj(pk, 'subscribe')

    @action(methods=('get',), detail=False)
    def subscriptions(self, request):
        """Список подписок пользоваетеля."""

        user = self.request.user
        authors = user.subscribe.all()
        pages = self.paginate_queryset(authors)
        serializer = serializers.UserSubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


@api_view(['POST'])
@permission_classes([drf_permissions.AllowAny])
def create_token(request):
    """Создание токена."""

    serializer = serializers.TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = User.objects.get(email=serializer.data['email'])
        if not check_password(serializer.data['password'], user.password):
            return Response(
                {"Данные авторизации предоставлены не верно."},
                status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken.for_user(user)
        return Response(
            {"auth_token": f"{token.access_token}"},
            status=status.HTTP_201_CREATED
        )
    except ObjectDoesNotExist:
        return Response(
            {"Пользователя с данным email не существует."},
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def delete_token(request):
    """Удаление токена."""
    
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для тэгов."""

    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer

    def get_paginated_response(self, data):
        """Возвращение данных без пагинации."""
        return Response(data)


class IngredientViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet
                                ):
    """Работет с игридиентами."""

    serializer_class = serializers.IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            queryset_start_with = models.Ingredient.objects.filter(
                name__istartswith=name)
            queryset_contains = models.Ingredient.objects.filter(
                name__icontains=name).exclude(id__in=queryset_start_with)
            return chain(queryset_start_with, queryset_contains)
        return models.Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet, AddDelViewMixin):
    """Работает с рецептами."""

    queryset = models.Recipe.objects.select_related('author')
    serializer_class = serializers.RecipeSerializer
    permission_classes = (permissions.AdminAuthorsReadOnly,)
    pagination_class = paginators.StandardResultsSetPagination
    add_serializer = serializers.ShortRecipeSerializer

    def get_queryset(self):
        """Получает queryset в соответствии с параметрами запроса."""
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if user.is_anonymous:
            return queryset

        is_in_shopping = self.request.query_params.get('author')
        if is_in_shopping in ('1', 'true',):
            queryset = queryset.filter(cart=user.id)
        elif is_in_shopping in ('0', 'false',):
            queryset = queryset.exclude(cart=user.id)

        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ('1', 'true',):
            queryset = queryset.filter(favorite=user.id)
        if is_favorited in ('0', 'false',):
            queryset = queryset.exclude(favorite=user.id)

        return queryset

    @action(methods=settings.ACTION_METHODS, detail=True)
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в избранное."""

        return self.add_del_obj(pk, 'favorite')

    @action(methods=settings.ACTION_METHODS, detail=True)
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в `список покупок."""

        return self.add_del_obj(pk, 'shopping_cart')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        """Загружает файл *.txt со списком покупок."""
        
        user = self.request.user
        if not user.carts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = models.AmountIngredient.objects.filter(
            recipe__in=(user.carts.values('id'))
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = (
            f'Список покупок для:\n\n{user.first_name}\n\n'
        )
        for ing in ingredients:
            shopping_list += (
                f'{ing["ingredient"]}: {ing["amount"]} {ing["measure"]}\n'
            )

        shopping_list += '\n\nПосчитано в Foodgram'

        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
