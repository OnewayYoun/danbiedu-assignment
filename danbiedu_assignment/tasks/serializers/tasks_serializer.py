from rest_framework import serializers

from tasks.models.tasks_model import Task, SubTask
from users.models.users_model import Team


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
        if len(teams) == 0:
            raise serializers.ValidationError("At least one team must be specified.")
        invalid_teams = set(teams) - set(self.valid_teams)
        if invalid_teams:
            raise serializers.ValidationError(f"Invalid team name(s): {', '.join(invalid_teams)}")
        return teams

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('create_user', 'team')


class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = '__all__'
