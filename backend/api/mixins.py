from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


class AddDelViewMixin:
    """Добавляет во Viewset дополнительные методы."""

    add_serializer = None

    def add_del_obj(self, obj_id, meneger):
        """Добавляет/удаляет связь через менеджер `model.many-to-many`."""
        assert self.add_serializer is not None, (
            f'{self.__class__.__name__} should include '
            'an `add_serializer` attribute.'
        )

        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        menegers = {
            'subscribe': user.subscribe,
            'favorite': user.favorites,
            'shopping_cart': user.carts,
        }
        meneger = menegers[meneger]

        obj = get_object_or_404(self.queryset, id=obj_id)
        serializer = self.add_serializer(
            obj, context={'request': self.request}
        )
        obj_exist = meneger.filter(id=obj_id).exists()

        if (self.request.method in ('GET', 'POST',)) and not obj_exist:
            meneger.add(obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if (self.request.method in ('DELETE',)) and obj_exist:
            meneger.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
