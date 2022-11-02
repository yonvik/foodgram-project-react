from rest_framework.filters import SearchFilter


class IngredientSearchFilterSet(SearchFilter):
    """Поиск по названию ингредиента."""
    
    search_param = 'name'
