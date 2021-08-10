import asyncio
import json
from django.db.models import F
from django.db import transaction
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

import mainapp.models as models
import mainapp.services as services


class ProjectConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        self.group_name = f"project_{self.scope['url_route']['kwargs']['project_id']}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        text_data = event.get('text', None)
        if text_data is None:
            return
        data = json.loads(text_data)
        operation = self.operations.get(data.get('operation', None), None)
        if operation is None:
            return
        await operation(self, event)

    async def websocket_disconnect(self, event):
        pass

    async def move_task(self, event):
        await self.send_message(event['text'])
        await self.save_task_move(event)

    async def move_task_group(self, event):
        await self.send_message(event['text'])
        await self.save_task_group_move(event)

    @database_sync_to_async
    def save_task_group_move(self, event):
        with transaction.atomic():
            project_id = self.scope['url_route']['kwargs']['project_id']
            data = json.loads(event['text'])
            moved_group = models.TaskGroup.objects.by_id_or_none(data.get('group_id', -1))
            if moved_group is None:
                return

            old_pos = moved_group.position
            new_pos = data['new_pos']
            task_group_number = models.TaskGroup.objects.number_in_project(project_id)
            if old_pos == new_pos or not services.values_between((old_pos, new_pos), -1, task_group_number):
                return

            if old_pos < new_pos:
                affected_groups = models.TaskGroup.objects.position_in_project_between(project_id, old_pos, new_pos + 1)
                affected_groups.update(position=F('position') - 1)
            else:
                affected_groups = models.TaskGroup.objects.position_in_project_between(project_id, new_pos - 1, old_pos)
                affected_groups.update(position=F('position') + 1)
            moved_group.position = new_pos
            moved_group.save()

    @database_sync_to_async
    def save_task_move(self, event):
        with transaction.atomic():
            data = json.loads(event['text'])
            moved_task = models.Task.objects.by_id_or_none(data.get('task_id', -1))
            if moved_task is None:
                return

            old_group = moved_task.task_group
            new_group = models.TaskGroup.objects.by_id_or_none(data.get('new_group_id', -1))
            if new_group is None:
                return

            old_pos = moved_task.position
            new_pos = data.get('new_pos', None)
            if new_pos is None or (old_group.id == new_group.id and old_pos == new_pos):
                return

            task_number_old_task_group = old_group.tasks.count()
            task_number_new_task_group = new_group.tasks.count()

            if not 0 <= old_pos <= task_number_old_task_group or \
                    not 0 <= new_pos <= task_number_new_task_group:
                return

            models.Task.objects.position_in_group_greater_than(old_group.id, old_pos)\
                .update(position=F('position') - 1)
            models.Task.objects.position_in_group_greater_than(new_group.id, new_pos-1)\
                .update(position=F('position') + 1)
            moved_task.task_group = new_group
            moved_task.position = new_pos
            moved_task.save()
            print('task moved!')

    async def send_message(self, text):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'broadcast_data',
                'text': text
            }
        )

    async def broadcast_data(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    operations = {
        'move_task_group': move_task_group,
        'move_task': move_task
    }
