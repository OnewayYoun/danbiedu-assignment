from rest_framework import serializers

from tasks.models.tasks_model import Task, SubTask
from users.models.users_model import Team


def validate_team_names(teams, valid_teams):
    if len(teams) == 0:
        raise serializers.ValidationError("At least one team must be specified.")
    invalid_teams = set(teams) - set(valid_teams)
    if invalid_teams:
        raise serializers.ValidationError(f"Invalid team name(s): {', '.join(invalid_teams)}")
    return teams


class SubTaskSerializer(serializers.ModelSerializer):
    team = serializers.CharField(source='team.name')

    class Meta:
        model = SubTask
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    valid_teams = ['단비', '다래', '블라블라', '철로', '땅이', '해태', '수피']
    teams = serializers.ListField(write_only=True)

    def create(self, validated_data):
        validated_data['create_user'] = self.context['user']
        validated_data['team'] = self.context['user'].team

        teams = validated_data.pop('teams', [])
        task = Task.objects.create(**validated_data)

        search_dict = {team.name: team.pk for team in Team.objects.filter(name__in=self.valid_teams)}
        subtasks = []
        for team in teams:
            subtasks.append(SubTask(task=task, team_id=search_dict[team]))
        SubTask.objects.bulk_create(subtasks)

        return task

    def validate_teams(self, teams):
        return validate_team_names(teams, self.valid_teams)

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('create_user', 'team')


class TaskListSerializer(serializers.ModelSerializer):
    team = serializers.CharField(source='team.name')
    subtasks = SubTaskSerializer(source='subtask_set', many=True)

    class Meta:
        model = Task
        fields = '__all__'


class TaskUpdateSerializer(serializers.ModelSerializer):
    valid_teams = ['단비', '다래', '블라블라', '철로', '땅이', '해태', '수피']
    teams = serializers.ListField(write_only=True)

    def update(self, instance, validated_data):
        teams = validated_data.get('teams')
        if teams is not None:
            instance.subtask_set.filter(is_complete=False).exclude(team__name__in=teams).delete()

            teams_to_add = set(teams) - set(instance.subtask_set.values_list('team__name', flat=True))
            if teams_to_add:
                search_dict = {team.name: team.pk for team in Team.objects.filter(name__in=self.valid_teams)}
                subtasks = []
                for team in teams_to_add:
                    subtasks.append(SubTask(task=instance, team_id=search_dict[team]))
                SubTask.objects.bulk_create(subtasks)
        return instance

    def validate_teams(self, teams):
        return validate_team_names(teams, self.valid_teams)

    class Meta:
        model = Task
        fields = ('title', 'content', 'teams')
