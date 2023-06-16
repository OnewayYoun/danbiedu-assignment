from django.db.transaction import atomic
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status, mixins

from tasks.serializers.tasks_serializer import (
    TaskSerializer, TaskListSerializer, SubTaskSerializer
)
from tasks.models.tasks_model import Task, SubTask
from tasks.permissions.tasks_permission import IsTaskOwner
from users.models.users_model import User


class TaskViewSet(mixins.UpdateModelMixin, GenericViewSet):
    queryset = Task.objects.select_related('team').prefetch_related('subtask_set', 'subtask_set__team').all()
    serializer_class = TaskSerializer
    permission_classes_by_action = dict(
        partial_update=[IsTaskOwner],
    )

    def get_permissions(self):
        permissions = self.permission_classes_by_action.get(
            self.action, self.permission_classes
        )
        return [permission() for permission in permissions]

    @atomic
    def create(self, request, *args, **kwargs):
        user = User.objects.select_related('team').get(id=request.user.pk)
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(subtask__team=request.user.team)
        serializer = TaskListSerializer(queryset, many=True)
        return Response(serializer.data)


class SubTaskViewSet(GenericViewSet):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
