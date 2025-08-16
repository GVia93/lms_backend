from django.contrib.auth.models import AbstractUser
from django.db import models


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

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """Возвращает email как строковое представление пользователя."""
        return self.email
