from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from users.serializers.users_serializer import UserSerializer, UserListSerializer
from users.models.users_model import User
from users.permissions.users_permission import IsUserOwner


class UserViewSet(GenericViewSet):
    queryset = User.objects.select_related('team').all()
    serializer_class = UserSerializer
    permission_classes_by_action = dict(
        create=[AllowAny],
        update=[IsUserOwner],
        retrieve=[IsUserOwner],
    )

    def get_permissions(self):
        permissions = self.permission_classes_by_action.get(
            self.action, self.permission_classes
        )
        return [permission() for permission in permissions]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserListSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"])
    def self(self, request, *args, **kwargs):
        user = self.queryset.get(id=request.user.pk)
        serializer = UserListSerializer(user)
        return Response(serializer.data)
