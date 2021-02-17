from django.conf import settings
from asgiref.sync import async_to_sync
from channels.consumer import SyncConsumer
from . import models

class StatusSyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        self.send({
            'type': 'websocket.accept'
        })

        self.send({
            'type': 'websocket.send',
            'text': str(models.Status.objects.first())
        })
        # Join ticks group
        async_to_sync(self.channel_layer.group_add)(
            "status",
            self.channel_name
        )

    def websocket_disconnect(self, event):
        # Leave ticks group
        async_to_sync(self.channel_layer.group_discard)(
            "status",
            self.channel_name
        )

    def new_status(self, event):
        self.send({
            'type': 'websocket.send',
            'text': event['content'],
        })

    