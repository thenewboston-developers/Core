import asyncio

import pytest
from channels.testing import WebsocketCommunicator
from django.utils import timezone

from core.core.utils.cryptography import generate_signature
from core.project.asgi import application


def make_token(private_key, public_key):
    now = timezone.now().isoformat()
    signature = generate_signature(now.encode('latin1'), private_key)
    return f'{public_key}${now}${signature}'


@pytest.mark.asyncio
async def test_can_set_and_get_peers(sender_key_pair, recipient_key_pair):
    communicator = WebsocketCommunicator(application, f'ws/accounts/{sender_key_pair.public}')
    connected, _ = await communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate sender
    await communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(sender_key_pair.private, sender_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # Set peers
    correlation_id = 'my-fake-random-correlation-id'
    peers = [recipient_key_pair.public]
    await communicator.send_json_to({'method': 'set_peers', 'peers': peers, 'correlation_id': correlation_id})
    assert await communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': correlation_id
    }

    # Get peers
    await communicator.send_json_to({'method': 'get_peers', 'correlation_id': correlation_id})
    assert await communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': False
        } for peer in peers},
        'correlation_id': correlation_id
    }

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_peer_connected_after_set_peers(sender_key_pair, recipient_key_pair):
    # Connect sender
    sender_communicator = WebsocketCommunicator(application, f'ws/accounts/{sender_key_pair.public}')
    connected, _ = await sender_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate sender
    await sender_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(sender_key_pair.private, sender_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # Set peers
    correlation_id = 'my-fake-random-correlation-id'
    peers = [recipient_key_pair.public]
    await sender_communicator.send_json_to({'method': 'set_peers', 'peers': peers, 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': correlation_id
    }

    # Get peers before recipient connection
    await sender_communicator.send_json_to({'method': 'get_peers', 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': False
        } for peer in peers},
        'correlation_id': correlation_id
    }

    # Connect recipient
    recipient_communicator = WebsocketCommunicator(application, f'ws/accounts/{recipient_key_pair.public}')
    connected, _ = await recipient_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate recipient
    await recipient_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(recipient_key_pair.private, recipient_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await recipient_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # Get online notification by sender
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': recipient_key_pair.public,
    }

    # Get peers
    await sender_communicator.send_json_to({'method': 'get_peers', 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': True
        } for peer in peers},
        'correlation_id': correlation_id
    }

    # Disconnect
    await recipient_communicator.disconnect()

    # Get offline notification by sender
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': recipient_key_pair.public,
    }

    # Get peers after recipient disconnection
    await sender_communicator.send_json_to({'method': 'get_peers', 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': False
        } for peer in peers},
        'correlation_id': correlation_id
    }

    await sender_communicator.disconnect()


@pytest.mark.asyncio
async def test_peer_connected_before_set_peers(sender_key_pair, recipient_key_pair):
    # Connect recipient
    recipient_communicator = WebsocketCommunicator(application, f'ws/accounts/{recipient_key_pair.public}')
    connected, _ = await recipient_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate recipient
    await recipient_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(recipient_key_pair.private, recipient_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await recipient_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # Connect sender
    sender_communicator = WebsocketCommunicator(application, f'ws/accounts/{sender_key_pair.public}')
    connected, _ = await sender_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate sender
    await sender_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(sender_key_pair.private, sender_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # Set peers
    correlation_id = 'my-fake-random-correlation-id'
    peers = [recipient_key_pair.public]
    await sender_communicator.send_json_to({'method': 'set_peers', 'peers': peers, 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': correlation_id
    }

    # TODO(dmu) MEDIUM: Is there a better way to make asyncio loop run?
    await asyncio.sleep(0.05)

    # Get peers
    await sender_communicator.send_json_to({'method': 'get_peers', 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': True
        } for peer in peers},
        'correlation_id': correlation_id
    }

    # Disconnect
    await recipient_communicator.disconnect()

    # Get offline notification by sender
    assert await sender_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': recipient_key_pair.public,
    }

    # Get peers after recipient disconnection
    await sender_communicator.send_json_to({'method': 'get_peers', 'correlation_id': correlation_id})
    assert await sender_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': False
        } for peer in peers},
        'correlation_id': correlation_id
    }

    await sender_communicator.disconnect()


@pytest.mark.asyncio
async def test_multiple_peers(sender_key_pair, recipient_key_pair, owner_key_pair):
    first_key_pair = sender_key_pair
    second_key_pair = recipient_key_pair
    third_key_pair = owner_key_pair

    # Connect first
    first_communicator = WebsocketCommunicator(application, f'ws/accounts/{first_key_pair.public}')
    connected, _ = await first_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate recipient
    await first_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(first_key_pair.private, first_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # First get peers
    await first_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await first_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {},
        'correlation_id': 'some-id'
    }

    # First sets peers
    first_peers = [second_key_pair.public, third_key_pair.public]
    await first_communicator.send_json_to({'method': 'set_peers', 'peers': first_peers, 'correlation_id': 'some-id'})
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': 'some-id'
    }

    await first_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await first_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {peer: {
            'is_online': False
        } for peer in first_peers},
        'correlation_id': 'some-id'
    }

    # Connect second
    second_communicator = WebsocketCommunicator(application, f'ws/accounts/{second_key_pair.public}')
    connected, _ = await second_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate sender
    await second_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(second_key_pair.private, second_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # First gets notified, because second has connected
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': second_key_pair.public,
    }

    # First gets peers
    await first_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await first_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {
            second_key_pair.public: {
                'is_online': True
            },
            third_key_pair.public: {
                'is_online': False
            },
        },
        'correlation_id': 'some-id'
    }

    # Second get peers
    await second_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await second_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {},
        'correlation_id': 'some-id'
    }

    # Second sets peers
    second_peers = [first_key_pair.public, third_key_pair.public]
    await second_communicator.send_json_to({'method': 'set_peers', 'peers': second_peers, 'correlation_id': 'some-id'})
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': 'some-id'
    }

    # TODO(dmu) MEDIUM: Is there a better way to make asyncio loop run?
    await asyncio.sleep(0.05)

    # Second gets peers
    await second_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await second_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {
            first_key_pair.public: {
                'is_online': True
            },
            third_key_pair.public: {
                'is_online': False
            },
        },
        'correlation_id': 'some-id'
    }

    # Connect third
    third_communicator = WebsocketCommunicator(application, f'ws/accounts/{third_key_pair.public}')
    connected, _ = await third_communicator.connect()
    assert connected

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate recipient
    await third_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(third_key_pair.private, third_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await third_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # First gets notified, because third has connected
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': third_key_pair.public,
    }

    # First gets peers
    await first_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await first_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {
            second_key_pair.public: {
                'is_online': True
            },
            third_key_pair.public: {
                'is_online': True
            },
        },
        'correlation_id': 'some-id'
    }

    # Second gets notified, because third has connected
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': third_key_pair.public,
    }

    # Second gets peers
    await second_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await second_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {
            first_key_pair.public: {
                'is_online': True
            },
            third_key_pair.public: {
                'is_online': True
            },
        },
        'correlation_id': 'some-id'
    }

    # Third gets peers
    await third_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await third_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {},
        'correlation_id': 'some-id'
    }

    # Third sets peers
    third_peers = [second_key_pair.public, first_key_pair.public]
    await third_communicator.send_json_to({'method': 'set_peers', 'peers': third_peers, 'correlation_id': 'some-id'})
    assert await third_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': 'some-id'
    }

    # TODO(dmu) MEDIUM: Is there a better way to make asyncio loop run?
    await asyncio.sleep(0.05)

    # Third gets peers
    await third_communicator.send_json_to({'method': 'get_peers', 'correlation_id': 'some-id'})
    assert await third_communicator.receive_json_from(timeout=0.03) == {
        'return_value': {
            first_key_pair.public: {
                'is_online': True
            },
            second_key_pair.public: {
                'is_online': True
            },
        },
        'correlation_id': 'some-id'
    }

    # First disconnects
    await first_communicator.disconnect()

    # Second gets notified, because first has disconnected
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': first_key_pair.public,
    }

    # Third gets notified, because first has disconnected
    assert await third_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': first_key_pair.public,
    }

    # First connects again
    first_communicator = WebsocketCommunicator(application, f'ws/accounts/{first_key_pair.public}')
    connected, _ = await first_communicator.connect()
    assert connected

    # Second and third do not receive anything before authentication
    await second_communicator.receive_nothing()
    await third_communicator.receive_nothing()

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate recipient
    await first_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(first_key_pair.private, first_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # Second gets notified, because first has connected
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': first_key_pair.public,
    }

    # Third gets notified, because first has connected
    assert await third_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': first_key_pair.public,
    }

    # Second removes first from peers
    second_peers = [third_key_pair.public]
    await second_communicator.send_json_to({'method': 'set_peers', 'peers': second_peers, 'correlation_id': 'some-id'})
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': 'some-id'
    }

    # First disconnects again
    await first_communicator.disconnect()

    # Second does not receive anything because first is no longer its peer
    await second_communicator.receive_nothing()

    # Third gets notified, because first has disconnected
    assert await third_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': first_key_pair.public,
    }

    # First connects again
    first_communicator = WebsocketCommunicator(application, f'ws/accounts/{first_key_pair.public}')
    connected, _ = await first_communicator.connect()
    assert connected

    # Second and third do not receive anything before authentication
    await second_communicator.receive_nothing()
    await third_communicator.receive_nothing()

    # TODO(dmu) HIGH: Make authentication DRY
    # Authenticate recipient
    await first_communicator.send_json_to({
        'method': 'authenticate',
        'token': make_token(first_key_pair.private, first_key_pair.public),
        'correlation_id': 'auth-correlation-id'
    })
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'return_value': True,
        'correlation_id': 'auth-correlation-id'
    }

    # First sets peers
    first_peers = [second_key_pair.public, third_key_pair.public]
    await first_communicator.send_json_to({'method': 'set_peers', 'peers': first_peers, 'correlation_id': 'some-id'})
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'return_value': None,
        'correlation_id': 'some-id'
    }

    # Third gets notified, because first has connected
    assert await third_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': True,
        'account_number': first_key_pair.public,
    }

    # Everybody disconnect in reverse order
    await third_communicator.disconnect()

    # First gets notified, because third has disconnected
    assert await first_communicator.receive_json_from(timeout=0.1) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': third_key_pair.public,
    }

    # Second gets notified, because third has disconnected
    assert await second_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': third_key_pair.public,
    }

    await second_communicator.disconnect()

    # First gets notified, because second has disconnected
    assert await first_communicator.receive_json_from(timeout=0.05) == {
        'type': 'track.online_status',
        'is_online': False,
        'account_number': second_key_pair.public,
    }

    await first_communicator.disconnect()


def _test_self_peering():
    raise NotImplementedError


def _test_multiple_connections_for_the_same_account():
    raise NotImplementedError
