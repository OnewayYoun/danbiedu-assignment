from django.urls import path, include
from rest_framework import routers
from users.views.users_view import UserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
