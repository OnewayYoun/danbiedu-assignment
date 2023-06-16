# Generated by Django 3.2 on 2023-06-16 03:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('is_complete', models.BooleanField(default=False)),
                ('completed_date', models.DateTimeField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('create_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.team')),
            ],
            options={
                'db_table': 'task',
            },
        ),
        migrations.CreateModel(
            name='SubTask',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_complete', models.BooleanField(default=False)),
                ('completed_date', models.DateTimeField(default=None)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tasks.task')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.team')),
            ],
            options={
                'db_table': 'sub_task',
            },
        ),
    ]
