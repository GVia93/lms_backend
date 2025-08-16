from django.db.models import Count
from rest_framework import generics, permissions, viewsets

from users.permissions import IsModer, IsOwner, ModerNoCreateNoDelete

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.

    Правила доступа:
    - Модераторы видят все курсы (но не могут создавать и удалять).
    - Обычные пользователи видят и управляют только своими курсами.
    - Удаление доступно только владельцу.
    """

    queryset = Course.objects.annotate(lessons_count=Count("lessons")).order_by("id")
    serializer_class = CourseSerializer

    def get_queryset(self):
        """Возвращает список курсов: всем модераторам или только свои для обычного пользователя."""
        u = self.request.user
        if u.is_authenticated and u.groups.filter(name="Модераторы").exists():
            return super().get_queryset()
        return super().get_queryset().filter(owner=u)

    def get_permissions(self):
        """
        Определяет права доступа:
        - просмотр/редактирование — модератор или владелец,
        - удаление — только владелец,
        - создание ограничено ModerNoCreateNoDelete.
        """
        perms = [permissions.IsAuthenticated, ModerNoCreateNoDelete]
        if self.action in ["retrieve", "update", "partial_update"]:
            perms.append(IsModer | IsOwner)
        elif self.action == "destroy":
            perms.append(IsOwner)
        return [p() if isinstance(p, type) else p for p in perms]

    def perform_create(self, serializer):
        """При создании курса автоматически назначает владельцем текущего пользователя."""
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    APIView для списка и создания уроков.

    Правила доступа:
    - Модераторы видят все уроки (но не могут создавать).
    - Обычные пользователи видят и создают только свои.
    """

    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, ModerNoCreateNoDelete]

    def get_queryset(self):
        """Возвращает список уроков: всем модераторам или только свои для обычного пользователя."""
        u = self.request.user
        if u.groups.filter(name="Модераторы").exists():
            return super().get_queryset()
        return super().get_queryset().filter(owner=u)

    def perform_create(self, serializer):
        """При создании урока автоматически назначает владельцем текущего пользователя."""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView для получения, обновления или удаления урока.

    Правила доступа:
    - Просмотр и редактирование: модератор или владелец.
    - Удаление: только владелец.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsModer | IsOwner]
