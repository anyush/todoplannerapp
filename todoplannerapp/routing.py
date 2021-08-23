from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from mainapp.consumers import ProjectConsumer

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r'^projects/(?P<project_id>\d+)/$', ProjectConsumer.as_asgi()),
                    url(r'^projects/(?P<project_id>\d+)/new_task_group/$', ProjectConsumer.as_asgi()),
                ]
            )
        )
    )
})
