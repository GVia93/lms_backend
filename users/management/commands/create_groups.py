from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Кастомная команда Django для создания группы 'Модераторы'.
    """

    help = "Создаёт группу 'Модераторы'"

    def handle(self, *args, **options):
        Group.objects.get_or_create(name="Модераторы")
        self.stdout.write(self.style.SUCCESS("Группа 'Модераторы' создана/существует"))
