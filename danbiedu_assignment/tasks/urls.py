from django.urls import path, include
from rest_framework import routers

from tasks.views.tasks_view import TaskViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"tasks", TaskViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
