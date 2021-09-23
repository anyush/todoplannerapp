import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

import mainapp.services as services
import mainapp.structures as structures


class ProjectConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.group_name = f"project_{self.scope['url_route']['kwargs']['project_id']}"

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, code):
        pass

    def receive_json(self, content, **kwargs):
        try:
            operation, structure = self.operations[content['operation']]
            context = json.loads(content['context'])
            context['user_id'] = self.scope['user'].id
            context['project_id'] = int(self.scope['url_route']['kwargs']['project_id'])
            context_struct = structure(**context)
            operation(self, context_struct, content)
        except (ValueError, KeyError) as e:
            print(e)
            return

    def receive_from_group(self, message):
        self.send(text_data=message['content'])

    def stream_message(self, content=None, text_content=None):
        if content is None and text_content is None:
            raise ValueError('Either content or text_content must be specified!')

        if text_content is None:
            text_content = json.dumps(content)

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'receive.from.group',
                'content': text_content
            }
        )

    def get_project_data(self, context_struct, content):
        project_data = services.get_project_page_data(context_struct.project_id)

        self.send(text_data=json.dumps({
            'operation': 'get_data',
            'context': project_data
        }))

    def create_task(self, context_struct, content):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'websocket.receive',
                'text': json.dumps({
                    'operation': 'get_data',
                    'context': '{}'
                })
            }
        )
        services.create_task(context_struct)

    def move_task(self, context_struct, content):
        self.stream_message(content=content)
        services.move_task(context_struct)

    def delete_task(self, context_struct, content):
        self.stream_message(content=content)
        services.delete_task(context_struct)

    def create_task_group(self, context_struct, content):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'websocket.receive',
                'text': json.dumps({
                    'operation': 'get_data',
                    'context': '{}'
                })
            }
        )
        services.create_task_group(context_struct)

    def modify_task_group(self, context_struct, content):
        self.stream_message(content=content)
        services.modify_task_group(context_struct)

    def move_task_group(self, context_struct, content):
        self.stream_message(content=content)
        services.move_task_group(context_struct)

    def delete_task_group(self, context_struct, content):
        self.stream_message(content=content)
        services.delete_task_group(context_struct)

    operations = {
        'get_data': (get_project_data, structures.ProjectStructure),
        'create_task': (create_task, structures.TaskCreateStructure),
        'move_task': (move_task, structures.TaskMoveStructure),
        'create_task_group': (create_task_group, structures.TaskGroupCreateStructure),
        'modify_task_group': (modify_task_group, structures.TaskGroupModifyStructure),
        'move_task_group': (move_task_group, structures.TaskGroupMoveStructure),
        'delete_task_group': (delete_task_group, structures.TaskGroupDeleteStructure),
    }
