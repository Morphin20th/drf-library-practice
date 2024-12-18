from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from user.views import CreateUserView, ManageUserView

urlpatterns = [
    path("", CreateUserView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_get"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ManageUserView.as_view(), name="manage"),
]

app_name = "user"
