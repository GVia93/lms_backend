from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с курсами.
    Поддерживает полный CRUD.
    """

    queryset = Course.objects.all().order_by("id")
    serializer_class = CourseSerializer


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    APIView для получения списка уроков и создания нового урока.
    """

    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView для получения, обновления или удаления конкретного урока.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
