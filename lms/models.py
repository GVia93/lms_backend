from django.conf import settings
from django.db import models


class Subscription(models.Model):
    """
    Модель подписки пользователя на курс.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        "lms.Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        unique_together = ("user", "course")
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курс"

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f"{self.user} → {self.course}"


class Course(models.Model):
    """
    Модель курса.
    Содержит название, описание, превью и владельца.
    """

    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to="course_previews/", blank=True, null=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    updated_at = models.DateTimeField(auto_now=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        """Возвращает название курса."""
        return self.title


class Lesson(models.Model):
    """
    Модель урока.
    Привязана к курсу и владельцу, содержит описание, превью и ссылку на видео.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preview = models.ImageField(upload_to="lesson_previews/", blank=True, null=True)
    video_url = models.URLField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        """Возвращает строку вида '<Курс>: <Урок>'."""
        return f"{self.course}: {self.title}"
