from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """
    Кастомная команда для создания суперпользователя
    с предопределёнными данными.
    """

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.create(email='admin@admin.com')
        user.set_password('admin')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user with email {user.email}'))