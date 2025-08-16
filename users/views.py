from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, viewsets
from rest_framework.filters import OrderingFilter

from .models import Payment
from .serializers import PaymentSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD для пользователей:
    - staff видят всех;
    - обычные пользователи — только себя.
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        u = self.request.user
        return User.objects.all() if u.is_staff else User.objects.filter(id=u.id)


class RegisterAPIView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    Доступна без авторизации.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class PaymentListAPIView(generics.ListAPIView):
    """
    API для получения списка платежей.
    Поддерживает фильтрацию и сортировку.
    """

    queryset = Payment.objects.select_related("user", "course", "lesson").order_by("-paid_at")
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method", "user"]
    ordering_fields = ["paid_at"]
