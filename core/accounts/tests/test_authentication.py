import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.utils import timezone

from core.accounts.consumers import MessageType, send
from core.core.utils.cryptography import generate_signature
from core.project.asgi import application


@pytest.mark.asyncio
async def test_authentication(sender_account_number, recipient_key_pair):
    communicator = WebsocketCommunicator(application, f'ws/accounts/{recipient_key_pair.public}')
    connected, _ = await communicator.connect()
    assert connected

    message = {
        'id': 'dc348eac-fc89-4b4e-96de-4a988e0b94e1',
        'sender': sender_account_number,
        'recipient': recipient_key_pair.public,
        'amount': 5,
        'transaction_fee': 1,
        'payload': {
            'message': 'Hey'
        }
    }
    await sync_to_async(send)(MessageType.CREATE_BLOCK, recipient_key_pair.public, message)
    assert await communicator.receive_nothing()

    now = timezone.now().isoformat()
    signature = generate_signature(now.encode('latin1'), recipient_key_pair.private)
    token = f'{recipient_key_pair.public}${now}${signature}'
    correlation_id = 'my-fake-random-correlation-id'
    await communicator.send_json_to({'method': 'authenticate', 'token': token, 'correlation_id': correlation_id})
    assert await communicator.receive_json_from(timeout=0.02) == {
        'return_value': True,
        'correlation_id': correlation_id
    }

    message = {
        'id': 'dc348eac-fc89-4b4e-96de-4a988e0b94e2',
        'sender': sender_account_number,
        'recipient': recipient_key_pair.public,
        'amount': 4,
        'transaction_fee': 2,
        'payload': {
            'message': 'Authenticated'
        }
    }
    await sync_to_async(send)(MessageType.CREATE_BLOCK, recipient_key_pair.public, message)

    assert await communicator.receive_json_from(timeout=0.01) == {
        'type': 'create.block',
        'message': message,
    }

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_invalid_token_authentication(sender_account_number, recipient_key_pair):
    communicator = WebsocketCommunicator(application, f'ws/accounts/{recipient_key_pair.public}')
    connected, _ = await communicator.connect()
    assert connected

    message = {
        'id': 'dc348eac-fc89-4b4e-96de-4a988e0b94e1',
        'sender': sender_account_number,
        'recipient': recipient_key_pair.public,
        'amount': 5,
        'transaction_fee': 1,
        'payload': {
            'message': 'Hey'
        }
    }
    await sync_to_async(send)(MessageType.CREATE_BLOCK, recipient_key_pair.public, message)
    assert await communicator.receive_nothing()

    correlation_id = 'my-fake-random-correlation-id'
    await communicator.send_json_to({'method': 'authenticate', 'token': 'invalid', 'correlation_id': correlation_id})
    assert await communicator.receive_json_from(timeout=0.01) == {
        'return_value': False,
        'correlation_id': correlation_id
    }

    message = {
        'id': 'dc348eac-fc89-4b4e-96de-4a988e0b94e2',
        'sender': sender_account_number,
        'recipient': recipient_key_pair.public,
        'amount': 4,
        'transaction_fee': 2,
        'payload': {
            'message': 'Authenticated'
        }
    }
    await sync_to_async(send)(MessageType.CREATE_BLOCK, recipient_key_pair.public, message)
    assert await communicator.receive_nothing()

    await communicator.disconnect()
