from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q

from lms.models import Course, Lesson


class UserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей.

    Используется для создания обычных пользователей и суперпользователей.
    Работает с кастомной моделью User, где email — основной идентификатор.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт и сохраняет обычного пользователя.
        """
        if not email:
            raise ValueError("Email обязателен")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Создаёт и сохраняет суперпользователя (администратора).
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя с авторизацией по email.
    Убирает стандартный username, добавляет телефон, город и аватар.
    """

    username = None
    email = models.EmailField("email", unique=True)

    phone = models.CharField("телефон", max_length=32, blank=True)
    city = models.CharField("город", max_length=120, blank=True)
    avatar = models.ImageField("аватар", upload_to="avatars/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает email как строковое представление пользователя."""
        return self.email


class Payment(models.Model):
    """
    Платёж за курс или урок.
    Ровно одно из полей: course или lesson должно быть заполнено (XOR).
    """

    class Method(models.TextChoices):
        """Возможные способы оплаты."""
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счёт"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    paid_at = models.DateTimeField("дата оплаты", auto_now_add=True)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, null=True, blank=True, related_name="payments"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(
        "сумма", max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid_at = models.DateTimeField("дата оплаты", auto_now_add=True, db_index=True)
    payment_method = models.CharField("способ оплаты", max_length=16, choices=Method.choices)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        constraints = [
            CheckConstraint(
                name="payment_one_target",
                check=(
                    (Q(course__isnull=False) & Q(lesson__isnull=True))
                    | (Q(course__isnull=True) & Q(lesson__isnull=False))
                ),
            )
        ]

    def __str__(self):
        """Возвращает строку с пользователем, объектом и суммой платежа."""
        target = self.course or self.lesson
        return f"{self.user} → {target} ({self.amount})"