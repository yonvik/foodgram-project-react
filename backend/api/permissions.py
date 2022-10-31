from rest_framework.permissions import (BasePermission,
                                        IsAuthenticatedOrReadOnly)


class AdminAuthorsReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение на изменения для автора или админа."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj.author)
            or request.user.is_staff
        )


class AdminOrReadOnly(BasePermission):
    """Разрешение на создание и изминения только админу."""
    def has_permission(self, request, view):
        return (
            request.method in ('GET',)
            or request.user.is_authenticated
            and request.user.is_admin
        )


class OwnerUserOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение на изминение только админу и пользователю."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj)
            or request.user.is_admin
        )
