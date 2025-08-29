from django.urls import reverse
from rest_framework.test import APITestCase

from lms.models import Course, Subscription
from users.models import User


class TestSubscription(APITestCase):
    """
    Набор тестов для проверки работы механизма подписки на курсы.
    """

    def setUp(self):
        """Создаёт пользователя, курс и выполняет авторизацию для тестов."""
        self.user = User.objects.create_user(email="u@test.com", password="pass12345")
        self.course = Course.objects.create(title="C1", owner=self.user)
        self.client.force_authenticate(self.user)

    def test_toggle_subscribe_unsubscribe(self):
        """
        Проверяет, что пользователь может подписаться и отписаться от курса.
        """
        url = reverse("lms:course-subscribe")

        # subscribe
        r1 = self.client.post(url, {"course": self.course.id}, format="json")
        self.assertEqual(r1.status_code, 200)
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

        # unsubscribe
        r2 = self.client.post(url, {"course": self.course.id}, format="json")
        self.assertEqual(r2.status_code, 200)
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_course_detail_has_is_subscribed(self):
        """
        Проверяет, что флаг `is_subscribed` присутствует и корректен
        в API-ответе детального представления курса.
        """
        Subscription.objects.create(user=self.user, course=self.course)
        r = self.client.get(reverse("lms:course-detail", args=[self.course.id]))
        self.assertEqual(r.status_code, 200)
        self.assertIn("is_subscribed", r.data)
        self.assertTrue(r.data["is_subscribed"])
