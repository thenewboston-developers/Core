from datetime import datetime, timedelta

import pytest
from channels.testing import WebsocketCommunicator
from django.utils import timezone

from core.core.utils.cryptography import generate_signature
from core.project.asgi import application


@pytest.mark.asyncio
async def test_can_connect_authenticated(sender_key_pair):
    now = timezone.now().isoformat()
    signature = generate_signature(now.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}${now}${signature}'
    communicator = WebsocketCommunicator(
        application,
        f'ws/accounts/{sender_key_pair.public}',
        headers=[(b'authorization', f'SToken {token}'.encode('latin1'))]
    )
    connected, _ = await communicator.connect()
    assert connected


@pytest.mark.asyncio
async def test_can_connect_naive_datetime_authenticated(sender_key_pair):
    now = datetime.utcnow()
    assert now.tzinfo is None
    now_str = now.isoformat()
    signature = generate_signature(now_str.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}${now_str}${signature}'
    communicator = WebsocketCommunicator(
        application,
        f'ws/accounts/{sender_key_pair.public}',
        headers=[(b'authorization', f'SToken {token}'.encode('latin1'))]
    )
    connected, _ = await communicator.connect()
    assert connected


@pytest.mark.asyncio
async def test_cannot_connect_unauthenticated_no_token(sender_key_pair):
    communicator = WebsocketCommunicator(application, f'ws/accounts/{sender_key_pair.public}')
    connected, _ = await communicator.connect()
    assert not connected


@pytest.mark.asyncio
async def test_cannot_connect_unauthenticated_invalid_token_format_1(sender_key_pair):
    communicator = WebsocketCommunicator(
        application,
        f'ws/accounts/{sender_key_pair.public}',
        headers=[(b'authorization', 'Token some_token'.encode('latin1'))]
    )
    connected, _ = await communicator.connect()
    assert not connected


@pytest.mark.asyncio
async def test_cannot_connect_unauthenticated_invalid_token_format_2(sender_key_pair):
    communicator = WebsocketCommunicator(
        application,
        f'ws/accounts/{sender_key_pair.public}',
        headers=[(b'authorization', 'Token fake$fake'.encode('latin1'))]
    )
    connected, _ = await communicator.connect()
    assert not connected


@pytest.mark.asyncio
async def test_cannot_connect_unauthenticated_invalid_datetime(sender_key_pair):
    now = timezone.now().isoformat()
    signature = generate_signature(now.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}$pokfoijeoif${signature}'
    communicator = WebsocketCommunicator(
        application,
        f'ws/accounts/{sender_key_pair.public}',
        headers=[(b'authorization', f'SToken {token}'.encode('latin1'))]
    )
    connected, _ = await communicator.connect()
    assert not connected


@pytest.mark.asyncio
async def test_cannot_connect_token_expired(sender_key_pair):
    token_time = (timezone.now() - timedelta(seconds=15)).isoformat()
    signature = generate_signature(token_time.encode('latin1'), sender_key_pair.private)
    token = f'{sender_key_pair.public}${token_time}${signature}'
    communicator = WebsocketCommunicator(
        application,
        f'ws/accounts/{sender_key_pair.public}',
        headers=[(b'authorization', f'SToken {token}'.encode('latin1'))]
    )
    connected, _ = await communicator.connect()
    assert not connected
