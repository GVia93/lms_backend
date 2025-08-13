from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Служит для отображения и создания платежей.
    """

    class Meta:
        model = Payment
        fields = ["id", "user", "paid_at", "course", "lesson", "amount", "payment_method"]
        read_only_fields = ["paid_at"]
