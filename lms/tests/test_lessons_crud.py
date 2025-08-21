from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import User


class TestLessonCRUD(APITestCase):
    """Интеграционные тесты CRUD для уроков с учётом ролей: владелец, модератор, другой пользователь."""

    def setUp(self):
        """Готовим группы, пользователей и стартовые данные."""
        # группы
        self.moder_group, _ = Group.objects.get_or_create(name="Модераторы")
        # пользователи
        self.owner = User.objects.create_user(email="owner@test.com", password="pass12345")
        self.other = User.objects.create_user(email="other@test.com", password="pass12345")
        self.moder = User.objects.create_user(email="moder@test.com", password="pass12345")
        self.moder.groups.add(self.moder_group)
        # данные
        self.course = Course.objects.create(title="C1", owner=self.owner)
        self.lesson = Lesson.objects.create(course=self.course, title="L1", owner=self.owner)

    def test_owner_full_crud(self):
        """Владелец может создать, обновить и удалить свой урок."""
        self.client.force_authenticate(self.owner)
        # create
        r_create = self.client.post(
            reverse("lms:lesson-list-create"),
            {"course": self.course.id, "title": "L2"},
            format="json",
        )
        self.assertEqual(r_create.status_code, 201, r_create.data)
        lid = r_create.data["id"]
        # update
        r_patch = self.client.patch(reverse("lms:lesson-rud", args=[lid]), {"title": "L2x"}, format="json")
        self.assertEqual(r_patch.status_code, 200, r_patch.data)
        # delete
        r_del = self.client.delete(reverse("lms:lesson-rud", args=[lid]))
        self.assertIn(r_del.status_code, (200, 204))

    def test_other_forbidden_modify_foreign(self):
        """Чужой пользователь не может редактировать или удалять чужой урок (403)."""
        self.client.force_authenticate(self.other)
        r_patch = self.client.patch(
            reverse("lms:lesson-rud", args=[self.lesson.id]),
            {"title": "Hack"},
            format="json",
        )
        self.assertEqual(r_patch.status_code, 403)
        r_del = self.client.delete(reverse("lms:lesson-rud", args=[self.lesson.id]))
        self.assertEqual(r_del.status_code, 403)

    def test_moder_edit_ok_but_create_delete_forbidden(self):
        """Модератор может редактировать чужой урок, но не может создавать и удалять."""
        self.client.force_authenticate(self.moder)
        # create запрещено (~IsModer)
        r_create = self.client.post(
            reverse("lms:lesson-list-create"),
            {"course": self.course.id, "title": "X"},
            format="json",
        )
        self.assertEqual(r_create.status_code, 403)
        # edit чужого урока — можно (IsModer | IsOwner)
        r_patch = self.client.patch(
            reverse("lms:lesson-rud", args=[self.lesson.id]),
            {"title": "L1_mod"},
            format="json",
        )
        self.assertEqual(r_patch.status_code, 200, r_patch.data)
        # delete запрещено
        r_del = self.client.delete(reverse("lms:lesson-rud", args=[self.lesson.id]))
        self.assertEqual(r_del.status_code, 403)
