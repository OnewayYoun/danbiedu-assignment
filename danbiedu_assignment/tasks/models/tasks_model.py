from django.db import models


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    create_user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    team = models.ForeignKey('users.Team', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    subtasks = models.ManyToManyField('SubTask', blank=True)

    class Meta:
        db_table = "task"


class SubTask(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey('users.Team', on_delete=models.CASCADE)
    is_complete = models.BooleanField(default=False)
    completed_date = models.DateTimeField(default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sub_task"
