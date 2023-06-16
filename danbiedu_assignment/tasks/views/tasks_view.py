from rest_framework.viewsets import GenericViewSet
from tasks.serializers.tasks_serializer import TaskSerializer
from tasks.models.tasks_model import Task


class TaskViewSet(GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
