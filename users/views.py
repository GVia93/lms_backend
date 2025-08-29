from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, views, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from .models import Payment
from .permissions import IsSelfOrStaff
from .serializers import (PaymentCheckoutSerializer, PaymentSerializer,
                          PrivateUserSerializer, PublicUserSerializer,
                          RegisterSerializer)
from .services import stripe_api

User = get_user_model()


class PaymentStatusAPIView(views.APIView):
    """
    Проверка статуса Stripe-сессии по её ID.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id: str):
        """
        Возвращает статус платежа из локальной БД и актуальный статус сессии из Stripe.
        """
        pay = get_object_or_404(Payment, stripe_session_id=session_id)

        if not (request.user.is_staff or pay.user_id == request.user.id):
            return Response({"detail": "Forbidden"}, status=403)

        data = stripe_api.retrieve_session(session_id)
        pay.status = data.get("status", pay.status)  # обновляем локальный статус
        pay.save(update_fields=["status"])

        return Response(
            {"status": pay.status, "stripe": {"id": data["id"], "status": data["status"]}}
        )


class PaymentCheckoutAPIView(views.APIView):
    """
    Создаёт Stripe Checkout-сессию для оплаты платежа и возвращает ссылку.

    Доступ: только владелец платежа или staff.
    Тело запроса: {"payment_id": <int>}
    Ответ: сериализованный Payment (id, amount, payment_method, checkout_url, status).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Инициирует оформление оплаты:
        - проверяет права;
        - при отсутствии сессии в Stripe создаёт Product, Price и Session;
        - возвращает данные платежа с checkout_url.
        """
        payment_id = request.data.get("payment_id")
        pay = get_object_or_404(Payment, pk=payment_id)

        if not (request.user.is_staff or pay.user_id == request.user.id):
            return Response({"detail": "Forbidden"}, status=403)

        # Название/описание продукта (курс или урок)
        target = pay.course or pay.lesson
        name = getattr(target, "title", "Оплата")
        description = f"Оплата за {'курс' if pay.course_id else 'урок'}: {name}"

        # Если сессии ещё нет — создаём Product, Price и Session
        if not pay.stripe_session_id:
            # Product
            prod_id = pay.stripe_product_id or stripe_api.create_product(name=name, description=description)
            pay.stripe_product_id = prod_id

            # Price
            price_id = pay.stripe_price_id or stripe_api.create_price(
                product_id=prod_id,
                amount=pay.amount,
                currency=settings.STRIPE_CURRENCY,
            )
            pay.stripe_price_id = price_id

            # Session
            sess_id, url = stripe_api.create_checkout_session(
                price_id=price_id,
                success_url=settings.STRIPE_SUCCESS_URL,
                cancel_url=settings.STRIPE_CANCEL_URL,
            )
            pay.stripe_session_id = sess_id
            pay.checkout_url = url
            pay.status = "open"
            pay.save(
                update_fields=[
                    "stripe_product_id",
                    "stripe_price_id",
                    "stripe_session_id",
                    "checkout_url",
                    "status",
                ]
            )

        ser = PaymentCheckoutSerializer(pay, context={"request": request})
        return Response(ser.data, status=200)


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
