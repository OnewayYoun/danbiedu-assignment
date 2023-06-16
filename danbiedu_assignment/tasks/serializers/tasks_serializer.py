from rest_framework import serializers
from tasks.models.tasks_model import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
