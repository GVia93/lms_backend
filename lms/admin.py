from django.contrib import admin

from .models import Course, Lesson, Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Админка для модели Subscription.
    Отображает список подписок на курсы.
    """

    list_display = ("id", "user", "course", "created_at")
    list_filter = ("course", "created_at")
    search_fields = ("user__email", "course__title")


class LessonInline(admin.TabularInline):
    """
    Инлайн-редактор уроков в админке курсов.
    Позволяет редактировать уроки прямо со страницы курса.
    """

    model = Lesson
    extra = 0
    fields = ("title", "video_url", "owner")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Course.
    Отображает список курсов с владельцем и количеством уроков.
    """

    list_display = ("id", "title", "owner", "lessons_count")
    list_filter = ("owner",)
    search_fields = ("title", "description", "owner__email")
    inlines = [LessonInline]

    @admin.display(description="Уроков")
    def lessons_count(self, obj):
        """Возвращает количество уроков, связанных с курсом."""
        return obj.lessons.count()


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Админ-панель для модели Lesson.
    Отображает список уроков с курсом и владельцем.
    """

    list_display = ("id", "title", "course", "owner")
    list_filter = ("course", "owner")
    search_fields = ("title", "course__title", "owner__email")
