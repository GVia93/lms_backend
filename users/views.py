from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter

from .models import Payment
from .permissions import IsSelfOrStaff
from .serializers import PaymentSerializer, PrivateUserSerializer, PublicUserSerializer, RegisterSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Управление профилями пользователей.

    Доступ:
    - Просмотр: любой аутентифицированный может видеть любой профиль (публичные поля).
    - Редактирование/удаление: только сам пользователь или staff (полные поля).
    """

    queryset = User.objects.all().order_by("id")
    permission_classes = [permissions.IsAuthenticated, IsSelfOrStaff]

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия и прав:
        - update/partial_update: PrivateUserSerializer
        - retrieve: PrivateUserSerializer для владельца/staff, иначе PublicUserSerializer
        - list/прочее: PublicUserSerializer
        """
        if self.action in ("update", "partial_update"):
            return PrivateUserSerializer
        if self.action == "retrieve":
            obj = self.get_object()
            return PrivateUserSerializer if (obj == self.request.user or self.request.user.is_staff) else PublicUserSerializer
        return PublicUserSerializer


class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    Доступна без авторизации.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class PaymentListAPIView(generics.ListAPIView):
    """
    API для списка платежей.
    - Staff видит все платежи.
    - Обычный пользователь видит только свои.
    Поддерживается фильтрация и сортировка.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["paid_at", "amount"]
    ordering = ["-paid_at"]

    def get_queryset(self):
        """Возвращает QuerySet с фильтрацией по пользователю, если он не staff."""
        qs = Payment.objects.select_related("user", "course", "lesson")
        return qs if self.request.user.is_staff else qs.filter(user=self.request.user)
