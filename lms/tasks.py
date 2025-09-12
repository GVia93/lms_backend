from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Course, Subscription


@shared_task
def send_course_update_emails(course_id: int):
    """
    Рассылает письма подписчикам курса об обновлении материалов.
    """
    course = Course.objects.filter(pk=course_id).first()
    if not course:
        return {"ok": False, "reason": "course_not_found"}

    emails = list(
        Subscription.objects.filter(course_id=course_id)
        .select_related("user")
        .values_list("user__email", flat=True)
    )
    if not emails:
        return {"ok": True, "sent": 0}

    subj = f"Обновление материалов курса: {course.title}"
    body = f"В курсе {course.title} появились обновления."
    sent = send_mail(subj, body, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=True)

    Course.objects.filter(pk=course_id).update(last_notified_at=timezone.now())
    return {"ok": True, "sent": sent, "course": course_id}
