from rest_framework import serializers

from users.models.users_model import User, Team


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    team_name = serializers.CharField(write_only=True)

    def create(self, validated_data):
        if validated_data["password"] != validated_data["confirm_password"]:
            raise serializers.ValidationError("password not matching")
        validated_data["password"] = validated_data.pop("confirm_password")
        team_name = validated_data.pop('team_name')
        try:
            team = Team.objects.get(name=team_name)
        except Team.DoesNotExist:
            raise serializers.ValidationError(f"team name with '{team_name}' does not exist")
        validated_data['team'] = team
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        team_name = validated_data.pop('team_name')
        try:
            team = Team.objects.get(name=team_name)
        except Team.DoesNotExist:
            raise serializers.ValidationError(f"team name with '{team_name}' does not exist")
        validated_data['team'] = team

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.set_password(validated_data.pop("password"))
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('username', 'password', 'confirm_password', 'team_name')


class UserListSerializer(serializers.ModelSerializer):
    team = serializers.CharField(source='team.name')

    class Meta:
        model = User
        fields = ('id', 'username', 'team')
