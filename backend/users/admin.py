from django.contrib.admin import ModelAdmin, register

from .models import User


@register(User)
class UserAdmin(ModelAdmin):
    """Предоставление категории пользователей в админке."""
    list_display = (
        'username', 'first_name', 'last_name', 'email',
    )
    fields = (
        ('username', 'email',),
        ('first_name', 'last_name',),
    )
    fieldsets = []
    search_fields = (
        'username', 'email',
    )
    list_filter = (
        'first_name', 'email'
    )
    save_on_top = True
