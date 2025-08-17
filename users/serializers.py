from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Payment

User = get_user_model()


class PublicUserSerializer(serializers.ModelSerializer):
    """Публичный профиль пользователя (без фамилии, пароля и истории платежей)."""

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "city", "avatar")


class PrivateUserSerializer(serializers.ModelSerializer):
    """Приватный профиль пользователя с полной информацией."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "payments",
        )


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации нового пользователя.
    Пароль хэшируется перед сохранением.
    """

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        )

    def create(self, validated_data):
        """Создаёт нового пользователя с хэшированным паролем."""
        pwd = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(pwd)
        user.save()
        return user


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Payment.
    Отображает данные о платеже и цель платежа (курс или урок).
    """

    target_type = serializers.SerializerMethodField()
    target_title = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = (
            "id",
            "amount",
            "payment_method",
            "paid_at",
            "course",
            "lesson",
            "target_type",
            "target_title",
        )
        read_only_fields = ("paid_at",)

    def get_target_type(self, obj):
        """Возвращает тип цели: course или lesson."""
        return "course" if obj.course else "lesson"

    def get_target_title(self, obj):
        """Возвращает название курса или урока, за который был платёж."""
        return obj.course.title if obj.course else obj.lesson.title
