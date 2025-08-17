from rest_framework.test import APITestCase

from lms.models import Course
from users.models import User


class TestLessonValidators(APITestCase):
    """
    Тесты для проверки валидации поля video_url в модели Lesson.

    Проверяем:
    - допускаются ссылки только на YouTube;
    - все остальные ссылки отклоняются.
    """

    @classmethod
    def setUpTestData(cls):
        """Создаём тестового пользователя и курс перед запуском тестов."""
        cls.user = User.objects.create_user(email="u@test.com", password="pass12345")
        cls.course = Course.objects.create(title="C1", owner=cls.user)

    def setUp(self):
        """Авторизуем пользователя и выставляем Bearer-токен."""
        resp = self.client.post(
            "/api/users/login/",
            {"email": "u@test.com", "password": "pass12345"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_accepts_youtube_link(self):
        """Урок с корректной YouTube-ссылкой должен успешно создаваться (201)."""
        r = self.client.post(
            "/api/lessons/",
            {
                "course": self.course.id,
                "title": "L1",
                "video_url": "https://youtu.be/abc123",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201, r.data)

    def test_rejects_non_youtube_link(self):
        """Урок с не-YouTube ссылкой должен отклоняться (400)."""
        r = self.client.post(
            "/api/lessons/",
            {
                "course": self.course.id,
                "title": "L2",
                "video_url": "https://vimeo.com/123",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400, r.data)
        self.assertIn("video_url", r.data)
