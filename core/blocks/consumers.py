from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer


class BlockConsumer(JsonWebsocketConsumer):

    def connect(self):
        """Accepts an incoming socket"""
        # TODO(dmu) MEDIUM: For some reason reusing websocket_connect() for adding groups to channel leads to
        #                   timeout error in unittest. Fix it
        account_number = self.scope['url_route']['kwargs']['account_number']
        async_to_sync(self.channel_layer.group_add)(self.group_name(account_number), self.channel_name)
        return super().connect()

    @staticmethod
    def group_name(account_number):
        """Name of group where messages will be broadcast"""
        return f'blocks_{account_number}'

    def send_block(self, event):
        """Send block to group"""
        self.send_json(event['message'])
