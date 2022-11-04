from django_filters.rest_framework import filters, NumberFilter, FilterSet

from rest_framework.filters import SearchFilter

from recipes.models import Tag, Recipe


class RecipeFilters(FilterSet):
    author = NumberFilter(field_name='author__id')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if int(value) == 1:
            return queryset.filter(favorite=self.request.user.id)

    def filter_shopping_cart(self, queryset, name, value):
        if int(value) == 1:
            return queryset.filter(cart=self.request.user.id)

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientSearchFilterSet(SearchFilter):
    """Поиск по названию ингредиента."""
    print('АОаоаооаа', flush=True)
    search_param = 'name'
