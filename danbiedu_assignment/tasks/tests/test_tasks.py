from rest_framework import status

from .test_setup import TaskTestSetUp
from users.models.users_model import User, Team
from tasks.models.tasks_model import Task, SubTask


class TestViews(TaskTestSetUp):
    def test_user_can_create_task(self):
        user = User.objects.get(team__name='수피')
        self.client.force_login(user)

        body_data = {'title': 'Sample Task', 'content': 'This is a test', 'teams': ['수피', '철로']}
        res = self.client.post(
            path=self.base_url,
            data=body_data,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        data = res.json()
        self.assertEqual(data['team'], user.team.id)

        subtasks = Task.objects.get(id=data['id']).subtask_set.all()
        subtask_cnt = subtasks.count()
        input_teams_cnt = len(body_data['teams'])
        self.assertEqual(subtask_cnt, input_teams_cnt)
        self.assertEqual(set(subtasks.values_list('team__name', flat=True)), set(body_data['teams']))

    def test_업무_생성_시_한_개_이상의_팀을_설정해야합니다(self):
        """
        업무 생성 시, 한 개 이상의 팀을 설정해야합니다.
        단, 업무(Task)를 생성하는 팀이 반드시 하위업무(SubTask)에 포함되지는 않습니다.
        ex) 단비 Team이 업무(Task) 생성 시 하위 업무로 단비, 다래, 철로 Team을 설정할 수 있습니다. 단, 단비팀이 업무를 진행하지 않아도
            될 경우에는 꼭 하위업무에 단비팀이 들어가지 않아도 됩니다.
        """
        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        body_data = {'title': 'Sample Task', 'content': 'This is a test', 'teams': []}
        res = self.client.post(
            path=self.base_url,
            data=body_data,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = res.json()
        self.assertEqual(*data['teams'], "At least one team must be specified.")

        body_data['teams'] = ['단비', '다래', '철로']
        res = self.client.post(
            path=self.base_url,
            data=body_data,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        body_data['teams'] = ['다래', '철로']
        res = self.client.post(
            path=self.base_url,
            data=body_data,
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_정해진_7개의_팀_이외에는_다른_팀에_하위업무를_부여할_수_없습니다(self):
        invalid_team_name = 'invalid_team'
        Team.objects.create(name=invalid_team_name)
        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        res = self.client.post(
            path=self.base_url,
            data={'title': 'Sample Task', 'content': 'This is a test', 'teams': [invalid_team_name]},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        data = res.json()
        self.assertEqual(*data['teams'], f'Invalid team name(s): {invalid_team_name}')

    def test_업무를_수정할_경우_하위업무의_팀들도_수정_가능합니다(self):
        """
        ex) 단비 Team이 업무(Task) 생성 시 하위 업무(SubTask)단비, 다래, 철로 Team을 설정 후 하위업무팀을 단비만 하도록 하거나
            단비, 다래, 수피 팀으로 유동적으로 변경가능합니다.
        """
        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        res = self.client.post(
            path=self.base_url,
            data={'title': 'Sample Task', 'content': 'This is a test', 'teams': ['단비', '다래', '철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        task_id = res.json()['id']
        teams_before_patch = set(Task.objects.get(id=task_id).subtask_set.values_list('team__name', flat=True))
        self.assertEqual({'단비', '다래', '철로'}, teams_before_patch)

        res = self.client.patch(
            path=self.base_url + '/' + str(task_id),
            data={'teams': ['철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        teams_after_patch = set(Task.objects.get(id=task_id).subtask_set.values_list('team__name', flat=True))
        self.assertNotEqual(teams_before_patch, teams_after_patch)
        self.assertEqual({'철로'}, teams_after_patch)

    def test_업무는_작성자_이외에_수정이_불가합니다(self):
        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        res = self.client.post(
            path=self.base_url,
            data={'title': 'Sample Task', 'content': 'This is a test', 'teams': ['단비', '다래', '철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        task_id = res.json()['id']
        user = User.objects.get(team__name='다래')
        self.client.force_login(user)

        res = self.client.patch(
            path=self.base_url + '/' + str(task_id),
            data={'teams': ['철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res.json()['detail'], 'You do not have permission to perform this action.')

    def test_해당_하위업무가_완료되었다면_삭제되지_않아야_합니다(self):
        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        res = self.client.post(
            path=self.base_url,
            data={'title': 'Sample Task', 'content': 'This is a test', 'teams': ['단비', '다래', '철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        task_id = res.json()['id']
        subtask_id = Task.objects.get(id=task_id).subtask_set.get(team__name='단비').id

        res = self.client.patch(
            path=self.base_url + '/' + str(task_id) + '/' + 'subtasks' + '/' + str(subtask_id),
            data={'is_complete': True},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        subtask = SubTask.objects.get(id=subtask_id)
        self.assertTrue(subtask.is_complete)

        res = self.client.patch(
            path=self.base_url + '/' + str(task_id),
            data={'teams': ['철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        teams_after_patch = set(Task.objects.get(id=task_id).subtask_set.values_list('team__name', flat=True))
        self.assertEqual(teams_after_patch, {'철로', '단비'})

    def test_업무의_모든_하위업무가_완료되면_해당_상위업무는_자동으로_완료처리가_되어야합니다(self):
        """
        하위업무(SubTask) 완료 처리는 소속된 팀만 처리 가능합니다
        """
        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        res = self.client.post(
            path=self.base_url,
            data={'title': 'Sample Task', 'content': 'This is a test', 'teams': ['철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        task_id = res.json()['id']
        task = Task.objects.get(id=task_id)
        self.assertFalse(task.is_complete)

        subtask_id = Task.objects.get(id=task_id).subtask_set.get(team__name='철로').id
        res = self.client.patch(
            path=self.base_url + '/' + str(task_id) + '/' + 'subtasks' + '/' + str(subtask_id),
            data={'is_complete': True},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        user = User.objects.get(team__name='철로')
        self.client.force_login(user)
        res = self.client.patch(
            path=self.base_url + '/' + str(task_id) + '/' + 'subtasks' + '/' + str(subtask_id),
            data={'is_complete': True},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        subtask = SubTask.objects.get(id=subtask_id)
        self.assertTrue(subtask.is_complete)
        task = Task.objects.get(id=task_id)
        self.assertTrue(task.is_complete)

    def test_업무_조회_시_하위업무에_본인_팀이_포함되어_있다면_업무목록에서_함께_조회가_가능해야합니다(self):
        """
        업무(Task) 조회 시 하위업무(SubTask)의 업무 처리여부를 확인할 수 있어야 합니다.
        """
        res = self.client.get(
            path=self.base_url
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(res.json()['detail'], 'Authentication credentials were not provided.')

        user = User.objects.get(team__name='단비')
        self.client.force_login(user)

        res = self.client.post(
            path=self.base_url,
            data={'title': 'Sample Task', 'content': 'This is a test', 'teams': ['철로']},
            format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(team__name='블라블라')
        self.client.force_login(user)
        res = self.client.get(
            path=self.base_url
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

        user = User.objects.get(team__name='철로')
        self.client.force_login(user)
        res = self.client.get(
            path=self.base_url
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(res.json()), 0)

        data = res.json()
        subtasks = data[0]['subtasks']
        for subtask in subtasks:
            self.assertIn('is_complete', subtask)
