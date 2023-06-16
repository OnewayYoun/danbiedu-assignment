from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def _create_user(self, **kwargs):
        user = self.model(**kwargs)
        user.set_password(kwargs["password"])
        user.save()
        return user

    def create_user(self, **kwargs):
        kwargs.setdefault("is_superuser", False)
        return self._create_user(**kwargs)

    def create_superuser(self, **kwargs):
        kwargs.setdefault("is_superuser", True)
        return self._create_user(**kwargs)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(unique=True, max_length=20)
    is_active = models.BooleanField(default=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username

    class Meta:
        db_table = "user"


class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "team"
