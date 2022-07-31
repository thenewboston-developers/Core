import logging
from enum import Enum

import channels.layers
from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

logger = logging.getLogger(__name__)


class MessageType(Enum):
    CREATE_BLOCK = 'create.block'
    UPDATE_ACCOUNT = 'update.account'


class AccountConsumer(JsonWebsocketConsumer):

    def connect(self):
        """Accepts an incoming socket"""
        # TODO(dmu) MEDIUM: For some reason reusing websocket_connect() for adding groups to channel leads to
        #                   timeout error in unittest. Fix it
        scope = self.scope
        authenticated_account_number = scope['authenticated_account_number']
        account_number = scope['url_route']['kwargs']['account_number']
        if not authenticated_account_number or authenticated_account_number != account_number:
            logger.info(
                '%s is not authorized to connect to %s', authenticated_account_number or 'Anonymous', account_number
            )
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(self.group_name(account_number), self.channel_name)
        return super().connect()

    @staticmethod
    def group_name(account_number):
        """Name of group where messages will be broadcast"""
        return f'blocks_{account_number}'

    def create_block(self, event):
        """Send block to group"""
        self.send_json(event)

    def update_account(self, event):
        """Send account to group"""
        self.send_json(event)


assert all(hasattr(AccountConsumer, item.value.replace('.', '_')) for item in MessageType)


def send(message_type: MessageType, recipient: str, message: dict):
    channel_layer = channels.layers.get_channel_layer()
    payload = {'type': message_type.value, 'message': message}
    async_to_sync(channel_layer.group_send)(AccountConsumer.group_name(recipient), payload)
