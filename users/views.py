from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import Payment
from .serializers import PaymentSerializer


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
