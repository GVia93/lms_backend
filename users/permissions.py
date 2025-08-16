from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """Доступ разрешён только владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "owner", None)
        return owner == request.user


class IsModer(BasePermission):
    """Разрешение для пользователей группы 'Модераторы'."""

    group_name = "Модераторы"

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.groups.filter(name=self.group_name).exists())


class ModerNoCreateNoDelete(BasePermission):
    """Модератор НЕ может create/delete."""

    def has_permission(self, request, view):

        is_moder = IsModer().has_permission(request, view)
        if not is_moder:
            return True
        return request.method not in ("POST", "DELETE")
