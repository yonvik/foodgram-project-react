from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('users', views.UserViewSet, 'users')
router_v1.register('tags', views.TagViewSet, 'tags')
router_v1.register('ingredients', views.IngredientViewSet, 'ingredients')
router_v1.register('recipes', views.RecipeViewSet, 'recipes')

auth_urls =[
    path('auth/token/logout/', views.delete_token, name='logout'),
    path('auth/token/login/', views.create_token, name='login'),
]

urlpatterns = (
    path('', include(router_v1.urls)),
    path('', include(auth_urls))
)
