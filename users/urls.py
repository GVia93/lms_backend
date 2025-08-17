from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentListAPIView, UserViewSet, RegisterAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


app_name = "users"
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
]