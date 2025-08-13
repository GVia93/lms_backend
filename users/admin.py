from django.contrib import admin

from .models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления пользовательской моделью User
    через интерфейс администратора. Отображает все поля модели.
    """

    exclude = ('password',)