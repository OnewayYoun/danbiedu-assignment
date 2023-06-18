from django.shortcuts import resolve_url
from rest_framework.test import APITestCase

from users.models.users_model import User, Team


class TaskTestSetUp(APITestCase):
    base_url = resolve_url(r'/api/tasks')
    valid_teams = ['단비', '다래', '블라블라', '철로', '땅이', '해태', '수피']

    @classmethod
    def __create_user(cls):
        users = [User(username=f'{team.name}_팀원', team_id=team.pk) for team in Team.objects.all()]
        User.objects.bulk_create(users)

    @classmethod
    def setUpTestData(cls):
        cls.__create_user()

    def tearDown(self):
        pass

