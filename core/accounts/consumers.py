import logging
from enum import Enum

import channels.layers
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import JsonWebsocketConsumer

from core.core.authentication import authenticate
from core.core.exceptions import NotAuthenticated

ACCOUNT_GROUP_TEMPLATE = 'account_{}'  # only the account owner is subscribed to this group
ONLINE_STATUS_TRACKING_GROUP_TEMPLATE = 'online_{}'  # peers subscribe to this channel for online status notifications

logger = logging.getLogger(__name__)


class MessageType(Enum):
    CREATE_BLOCK = 'create.block'
    UPDATE_ACCOUNT = 'update.account'
    HANDLE_PING = 'handle.ping'
    TRACK_ONLINE_STATUS = 'track.online_status'


class AccountConsumer(JsonWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_number = None
        self.peer_channels: dict[str, set[str]] = {}

    def connect(self):
        self.account_number = self.scope['url_route']['kwargs']['account_number']
        logger.debug('%s connected with channel name: %s', self.account_number, self.channel_name)
        return super().connect()

    def disconnect(self, code):
        self.send_to_group(
            ONLINE_STATUS_TRACKING_GROUP_TEMPLATE.format(self.account_number),
            self.make_online_tracking_payload(False),
        )
        super().disconnect(code)
        raise StopConsumer

    # Group management
    def add_to_group(self, group_name):
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)

    def add_to_account_group(self):
        self.add_to_group(ACCOUNT_GROUP_TEMPLATE.format(self.account_number))

    def add_to_online_status_tracking_group(self, account_number):
        self.add_to_group(ONLINE_STATUS_TRACKING_GROUP_TEMPLATE.format(account_number))

    def remove_from_online_status_tracking_group(self, account_number):
        async_to_sync(self.channel_layer.group_discard)(
            ONLINE_STATUS_TRACKING_GROUP_TEMPLATE.format(account_number),
            self.channel_name,
        )

    # Sending
    def send_to_group(self, group_name, payload):
        logger.debug('Sending to group %s: %s', group_name, payload)
        async_to_sync(self.channel_layer.group_send)(group_name, payload)

    def send_ping(self, account_number, is_silent=False):
        """Send ping to the account group if there is at least one connection on the other side it will respond"""
        self.send_to_group(
            ACCOUNT_GROUP_TEMPLATE.format(account_number),
            {
                'type': MessageType.HANDLE_PING.value,
                'pong_to_channel_name': self.channel_name,
                'is_silent': is_silent,
            },
        )

    def make_online_tracking_payload(self, is_online: bool, is_silent=False):
        return {
            'type': MessageType.TRACK_ONLINE_STATUS.value,
            'is_online': is_online,
            'is_silent': is_silent,
            'account_number': self.account_number,
            'channel_name': self.channel_name,
        }

    # RPC-methods
    def rpc_authenticate(self, token):
        if not (account_number := authenticate(token)) or account_number != self.account_number:
            return False

        self.add_to_account_group()
        self.send_to_group(
            ONLINE_STATUS_TRACKING_GROUP_TEMPLATE.format(self.account_number),
            self.make_online_tracking_payload(True),
        )
        return True

    def rpc_set_peers(self, *, peers):
        if not self.account_number:
            raise NotAuthenticated()

        peers = set(peers)
        peer_channels = self.peer_channels
        current_peers = peer_channels.keys()

        for peer_account_number in current_peers - peers:
            # Remove self from online group to stop tracking online status
            logger.debug('No longer tracking: %s', peer_account_number)
            self.remove_from_online_status_tracking_group(peer_account_number)
            del peer_channels[peer_account_number]

        for peer_account_number in peers - current_peers:
            logger.debug('Starting tracking: %s', peer_account_number)
            peer_channels[peer_account_number] = set()
            # Add self to online group to start receiving online/offline notifications
            self.add_to_online_status_tracking_group(peer_account_number)
            self.send_ping(peer_account_number, is_silent=True)

    def rpc_get_peers(self):
        if not self.account_number:
            raise NotAuthenticated()

        return {
            account_number: {
                'is_online': bool(channel_names)
            } for account_number, channel_names in self.peer_channels.items()
        }

    def send_rpc_response(self, response, correlation_id):
        self.send_json(response | {'correlation_id': correlation_id})

    def receive_json(self, content, **kwargs):
        correlation_id = content.pop('correlation_id', None)
        method_name = content.pop('method', None)
        if not method_name:
            logger.warning('Method is not provided')
            return

        rpc_method_name = f'rpc_{method_name}'
        if not (method := getattr(self, rpc_method_name, None)):
            logger.warning(f'{rpc_method_name}(...) is not defined')
            self.send_rpc_response({'error': 'not such method'}, correlation_id)
            return

        try:
            return_value = method(**content)
        except Exception:
            logger.exception('Error when calling %s(...)', method_name)
            self.send_rpc_response({'error': 'exception'}, correlation_id)
            return

        self.send_rpc_response({'return_value': return_value}, correlation_id)

    # Handlers
    def create_block(self, event):
        """Send block to group"""
        self.send_json(event)

    def update_account(self, event):
        """Send account to group"""
        self.send_json(event)

    def track_online_status(self, event):
        logger.debug('Got event in channel %s (account_number: %s): %s', self.channel_name, self.account_number, event)
        from_account = event['account_number']
        if (account_channels := self.peer_channels.get(from_account)) is None:
            logger.warning('Got notification for non-tracking account: %s', event)
            return

        from_channel = event['channel_name']
        if event['is_online']:
            account_channels.add(from_channel)
        else:
            account_channels.discard(from_channel)

        if not event.pop('is_silent', False):
            del event['channel_name']
            self.send_json(event)

    def handle_ping(self, event):
        channel_name = event['pong_to_channel_name']
        payload = self.make_online_tracking_payload(True, is_silent=event.get('is_silent', False))
        logger.debug('Sending to channel %s: %s', channel_name, payload)
        async_to_sync(self.channel_layer.send)(channel_name, payload)


assert all(hasattr(AccountConsumer, item.value.replace('.', '_')) for item in MessageType)


def send(message_type: MessageType, recipient: str, message: dict):
    channel_layer = channels.layers.get_channel_layer()
    payload = {'type': message_type.value, 'message': message}
    async_to_sync(channel_layer.group_send)(ACCOUNT_GROUP_TEMPLATE.format(recipient), payload)
