from django_filters.rest_framework import FilterSet, NumberFilter, filters
from recipes import models
from rest_framework.filters import SearchFilter


class RecipeFilters(FilterSet):
    author = NumberFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=models.Tag.objects.all()
    )
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorite=self.request.user.id)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(cart=self.request.user.id)
        return queryset

    class Meta:
        model = models.Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientSearchFilterSet(SearchFilter):
    """Поиск по названию ингредиента."""
    search_param = 'name'
