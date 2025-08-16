from django.db import models


class Course(models.Model):
    """
    Модель курса.
    Содержит название, описание и превью-изображение.
    """

    title = models.CharField(max_length=255)
    preview = models.ImageField(upload_to="course_previews/", blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        """Возвращает название курса."""
        return self.title


class Lesson(models.Model):
    """
    Модель урока.
    Связана с курсом, содержит название, описание, превью и ссылку на видео.
    """

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    preview = models.ImageField(upload_to="lesson_previews/", blank=True, null=True)
    video_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        """Возвращает строку вида '<Курс>: <Урок>'."""
        return f"{self.course}: {self.title}"
