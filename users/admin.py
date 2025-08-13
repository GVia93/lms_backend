from django.contrib import admin
from .models import User, Payment


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Админ-класс для управления пользовательской моделью User
    через интерфейс администратора. Отображает все поля модели.
    """

    exclude = ('password',)


    @admin.register(Payment)
    class PaymentAdmin(admin.ModelAdmin):
        """
        Админ-панель для модели Payment.
        Отображает платежи, позволяет фильтровать и искать по email пользователя.
        """
        
        list_display = ("id", "user", "paid_at", "course", "lesson", "amount", "payment_method")
        list_filter = ("payment_method", "paid_at")
        search_fields = ("user__email",)
