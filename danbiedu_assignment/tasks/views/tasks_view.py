from django.db.transaction import atomic
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status

from tasks.serializers.tasks_serializer import TaskSerializer, SubTaskSerializer
from tasks.models.tasks_model import Task, SubTask
from users.models.users_model import User


class TaskViewSet(GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    @atomic
    def create(self, request, *args, **kwargs):
        user = User.objects.select_related('team').get(id=request.user.pk)
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubTaskViewSet(GenericViewSet):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
