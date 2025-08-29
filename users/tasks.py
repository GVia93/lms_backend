from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q

User = get_user_model()


@shared_task
def deactivate_inactive_users():
    """
    Деактивирует пользователей, не заходивших более 30 дней
    (или ни разу не заходивших).
    """
    cutoff = timezone.now() - timedelta(days=30)
    qs = User.objects.filter(is_active=True).filter(Q(last_login__lt=cutoff) | Q(last_login__isnull=True))
    updated = qs.update(is_active=False)
    return {"ok": True, "deactivated": updated}
