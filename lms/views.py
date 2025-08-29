from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, views, viewsets
from rest_framework.response import Response

from users.permissions import IsModer, IsOwner

from .models import Course, Lesson, Subscription
from .paginators import DefaultPageNumberPagination
from .serializers import CourseSerializer, LessonSerializer


class SubscriptionToggleAPIView(views.APIView):
    """
    Переключение подписки пользователя на курс.
    POST:
      - если подписка существует — удалить;
      - если нет — создать.
    Ответ: {message, course, is_subscribed}.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Создаёт или удаляет подписку текущего пользователя на указанный курс."""
        course = get_object_or_404(Course, pk=request.data.get("course"))
        qs = Subscription.objects.filter(user=request.user, course=course)

        if qs.exists():
            qs.delete()
            return Response({"message": "подписка удалена", "course": course.id, "is_subscribed": False})

        Subscription.objects.create(user=request.user, course=course)
        return Response({"message": "подписка добавлена", "course": course.id, "is_subscribed": True})


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления курсами.

    Правила доступа:
    - Модераторы видят все курсы (но не могут создавать и удалять).
    - Обычные пользователи видят и управляют только своими курсами.
    - Удаление доступно только владельцу.
    """

    queryset = Course.objects.annotate(lessons_count=Count("lessons")).order_by("id").prefetch_related("lessons")
    serializer_class = CourseSerializer
    pagination_class = DefaultPageNumberPagination

    def get_serializer_context(self):
        """
        Добавляем в контекст сериализатора объект request.
        Это позволяет сериализатору знать, какой пользователь сделал запрос.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        """
        Возвращает сериализатор для текущего действия:
        - retrieve → детальный сериализатор с полным списком уроков;
        - остальные действия → базовый CourseSerializer.
        """

        if self.action == "retrieve":

            class CourseDetailSerializer(CourseSerializer):
                """Детальный сериализатор курса со списком уроков."""
                lessons = LessonSerializer(many=True, read_only=True)

            return CourseDetailSerializer
        return CourseSerializer

    def get_queryset(self):
        """Возвращает список курсов: всем модераторам или только свои для обычного пользователя."""
        u = self.request.user
        if u.is_authenticated and u.groups.filter(name="Модераторы").exists():
            return super().get_queryset()
        return super().get_queryset().filter(owner=u)

    def get_permissions(self):
        """
        Правила доступа:
        - list: IsAuthenticated
        - create: IsAuthenticated и НЕ модератор
        - update/partial_update/retrieve: модератор ИЛИ владелец
        - destroy: только владелец
        """
        if self.action == "list":
            perms = [permissions.IsAuthenticated]
        elif self.action == "create":
            perms = [permissions.IsAuthenticated, ~IsModer]
        elif self.action in ("update", "partial_update", "retrieve"):
            perms = [permissions.IsAuthenticated, IsModer | IsOwner]
        else:
            perms = [permissions.IsAuthenticated, IsOwner]
        return [p() for p in perms]

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
    pagination_class = DefaultPageNumberPagination

    def get_permissions(self):
        """GET — IsAuthenticated; POST — IsAuthenticated и НЕ модератор."""
        if self.request.method == "GET":
            perms = [permissions.IsAuthenticated]
        else:
            perms = [permissions.IsAuthenticated, ~IsModer]
        return [p() for p in perms]

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

    def get_permissions(self):
        """Для DELETE — только владелец; для остальных — базовые правила класса."""
        if self.request.method == "DELETE":
            self.permission_classes = [permissions.IsAuthenticated, IsOwner]
        return super().get_permissions()
