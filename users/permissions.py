from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsSelfOrStaff(BasePermission):
    """
    Доступ к изменению профиля:
    - сам пользователь,
    - либо staff.
    Просматривать (SAFE_METHODS) можно любой профиль.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (obj == request.user) or bool(request.user and request.user.is_staff)

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwner(BasePermission):
    """Доступ разрешён только владельцу объекта (по полю owner)."""

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, "owner", None)
        return owner == request.user


class IsModer(BasePermission):
    """Доступ для пользователей из группы 'Модераторы'."""

    group_name = "Модераторы"

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.groups.filter(name=self.group_name).exists())


class ModerNoCreateNoDelete(BasePermission):
    """Модератор НЕ может создавать и удалять объекты (POST/DELETE)."""

    def has_permission(self, request, view):
        is_moder = IsModer().has_permission(request, view)
        if not is_moder:
            return True
        return request.method not in ("POST", "DELETE")
