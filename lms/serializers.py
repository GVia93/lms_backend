from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_url


class ShortLessonSerializer(serializers.ModelSerializer):
    """
    Короткий сериализатор для модели Lesson.
    Используется для отображения только идентификатора и названия урока.
    """

    class Meta:
        model = Lesson
        fields = ("id", "title")


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Возвращает полную информацию об уроке.
    """

    video_url = serializers.URLField(
        required=False, allow_blank=True, validators=[validate_youtube_url]
    )

    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "description", "preview", "video_url"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    Включает связанные уроки в поле `lessons`.
    """

    lessons = ShortLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "preview", "description", "lessons_count", "lessons"]
