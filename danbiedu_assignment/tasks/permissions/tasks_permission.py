from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from tasks.models.tasks_model import SubTask


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.create_user == request.user


class IsInSubTaskTeam(BasePermission):
    def has_object_permission(self, request, view, obj):
        subtask_id = view.kwargs.get('subtask_pk')
        subtask = get_object_or_404(SubTask, id=subtask_id, task=obj)
        return request.user.team == subtask.team
