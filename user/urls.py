from django.urls import path

from user.views import CreateUserView

urlpatterns = [
    path("", CreateUserView.as_view(), name="register"),
]

app_name = "user"
