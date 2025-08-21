from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView, SubscriptionToggleAPIView


app_name = "lms"

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("courses/subscribe/", SubscriptionToggleAPIView.as_view(), name="course-subscribe"),
    path("", include(router.urls)),
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonRetrieveUpdateDestroyAPIView.as_view(), name="lesson-rud"),
]
