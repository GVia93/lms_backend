from .models import Payment
from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения информации о пользователе.
    """

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar")
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Хэширует пароль перед сохранением.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "phone", "city", "avatar")

    def create(self, validated_data):
        pwd = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Служит для отображения и создания платежей.
    """

    class Meta:
        model = Payment
        fields = ["id", "user", "paid_at", "course", "lesson", "amount", "payment_method"]
        read_only_fields = ["paid_at"]
