from django.test import TestCase
from django.contrib.auth.models import User

import mainapp.models as models
import mainapp.structures as structures
import mainapp.services as services


class TaskTests(TestCase):
    tasks_created = 0

    @classmethod
    def setUpTestData(cls):
        cls.users = (User.objects.create_user("nickname"), )
        cls.projects = (models.Project.objects.create(
            name='project_name',
            owner=cls.users[0],
        ), )
        cls.projects[0].members.set(cls.users)
        cls.task_groups = (
            models.TaskGroup.objects.create(
                name='group_name_0',
                project=cls.projects[0],
                color='#000000',
                task_color='#000000',
                position=0
            ),
            models.TaskGroup.objects.create(
                name='group_name_1',
                project=cls.projects[0],
                color='#000000',
                task_color='#000000',
                position=1
            ))

    def create_task(self, user_id=None, project_id=None, group_id=None, name=None):
        context_struct = self.get_creation_context_struct(user_id, project_id, group_id, name)
        task_id, created = services.create_task(context_struct)

        if created:
            self.tasks_created += 1
        return task_id, created

    def get_creation_context_struct(self, user_id, project_id, group_id, name):
        user_id = user_id if user_id is not None else self.users[0].id
        project_id = project_id if project_id is not None else self.projects[0].id
        group_id = group_id if group_id is not None else self.task_groups[0].id
        name = name if name is not None else f'task_name_{self.tasks_created}'

        return structures.TaskCreateStructure(
                user_id=user_id,
                project_id=project_id,
                group_id=group_id,
                name=name,
            )

    def test_creation(self):
        task_id, created = self.create_task()
        self.assertTrue(created, 'Task has not been created!')
        try:
            models.Task.objects.get(id=task_id)
        except models.Task.DoesNotExist:
            self.fail('Task has not been created or id is not valid!')

    def test_move_inside_group(self):
        task_ids = tuple(map(lambda tpl: tpl[0] if tpl[1] else self.fail('Task has not been created'),
                             (self.create_task() for _ in range(2))))

        context_struct = structures.TaskMoveStructure(
            user_id=self.users[0].id,
            project_id=self.projects[0].id,
            task_id=task_ids[0],
            new_group_id=self.task_groups[0].id,
            new_pos=1
        )

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).position, 0)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).position, 1)

        services.move_task(context_struct)

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).position, 1)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).position, 0)

    def test_move_to_different_group(self):
        task_ids = tuple(map(lambda tpl: tpl[0] if tpl[1] else self.fail('Task has not been created!'),
                             (self.create_task(),
                              self.create_task(),
                              self.create_task(group_id=self.task_groups[1].id)
                              )))

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).task_group.id, self.task_groups[0].id)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).task_group.id, self.task_groups[0].id)
        self.assertEqual(models.Task.objects.get(id=task_ids[2]).task_group.id, self.task_groups[1].id)

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).position, 0)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).position, 1)
        self.assertEqual(models.Task.objects.get(id=task_ids[2]).position, 0)

        context_struct = structures.TaskMoveStructure(
            user_id=self.users[0].id,
            project_id=self.projects[0].id,
            task_id=task_ids[0],
            new_group_id=self.task_groups[1].id,
            new_pos=0
        )

        services.move_task(context_struct)

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).task_group.id, self.task_groups[1].id)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).task_group.id, self.task_groups[0].id)
        self.assertEqual(models.Task.objects.get(id=task_ids[2]).task_group.id, self.task_groups[1].id)

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).position, 0)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).position, 0)
        self.assertEqual(models.Task.objects.get(id=task_ids[2]).position, 1)

        context_struct = structures.TaskMoveStructure(
            user_id=self.users[0].id,
            project_id=self.projects[0].id,
            task_id=task_ids[0],
            new_group_id=self.task_groups[0].id,
            new_pos=1
        )

        services.move_task(context_struct)

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).task_group.id, self.task_groups[0].id)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).task_group.id, self.task_groups[0].id)
        self.assertEqual(models.Task.objects.get(id=task_ids[2]).task_group.id, self.task_groups[1].id)

        self.assertEqual(models.Task.objects.get(id=task_ids[0]).position, 1)
        self.assertEqual(models.Task.objects.get(id=task_ids[1]).position, 0)
        self.assertEqual(models.Task.objects.get(id=task_ids[2]).position, 0)

    def test_deletion(self):
        task_id, created = self.create_task()
        self.assertTrue(created)
        try:
            models.Task.objects.get(id=task_id)
        except models.Task.DoesNotExist:
            self.fail('Task has not been created')

        context_struct = structures.TaskDeleteStructure(
            user_id=self.users[0].id,
            project_id=self.projects[0].id,
            task_id=task_id
        )

        services.delete_task(context_struct)
        self.assertRaises(models.Task.DoesNotExist, models.Task.objects.get, id=task_id)
