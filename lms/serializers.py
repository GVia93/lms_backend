from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Возвращает полную информацию об уроке.
    """

    class Meta:
        model = Lesson
        fields = ["id", "course", "title", "description", "preview", "video_url"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Course.
    Включает связанные уроки в поле `lessons`.
    """

    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "preview", "description", "lessons_count", "lessons"]
