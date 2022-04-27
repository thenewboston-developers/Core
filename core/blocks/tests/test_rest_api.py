from unittest.mock import patch

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from model_bakery import baker

from core.accounts.models import Account
from core.blocks.models import Block
from core.blocks.views.block import send as block_send
from core.config.asgi import application
from core.core.utils.cryptography import sign_dict


@pytest.mark.parametrize('does_recipient_exist', (False, True))
def test_create_block(sender_key_pair, sender_account, recipient_account_number, does_recipient_exist, api_client):
    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()
    if does_recipient_exist:
        recipient_initial_balance = 1000
        baker.make('accounts.Account', account_number=recipient_account_number, balance=recipient_initial_balance)
    else:
        recipient_initial_balance = 0

    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    with patch('core.blocks.views.block.send') as send_mock:
        response = api_client.post('/api/blocks', payload)

    assert response.status_code == 201
    response_json = response.json()
    assert isinstance(response_json.pop('id'), int)
    assert response_json == payload
    query = Block.objects.filter(sender=payload['sender'])
    assert query.count() == 1
    block = query.get()
    assert block.sender == payload['sender']
    assert block.recipient == payload['recipient']
    assert block.amount == payload['amount']
    assert block.payload == payload['payload']
    assert block.signature == payload['signature']

    recipient_account = Account.objects.get(account_number=recipient_account_number)
    assert recipient_account.balance == recipient_initial_balance + 5

    send_mock.assert_called_once_with(dict(payload, id=block.id))


@pytest.mark.asyncio
async def test_block_send(recipient_account_number):
    communicator = WebsocketCommunicator(application, f'ws/blocks/{recipient_account_number}')
    connected, _ = await communicator.connect()
    assert connected

    message_to_send = {'message': 'Hi', 'recipient': recipient_account_number}
    await sync_to_async(block_send)(message_to_send)

    received_message = await communicator.receive_json_from()
    assert message_to_send == received_message

    await communicator.disconnect()


@pytest.mark.django_db
def test_cannot_create_block_if_sender_account_does_not_exist(
    sender_key_pair, sender_account_number, recipient_account_number, api_client
):
    assert not Account.objects.filter(account_number=sender_account_number).exists()

    payload = {
        'sender': sender_account_number,
        'recipient': recipient_account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    response = api_client.post('/api/blocks', payload)
    assert response.status_code == 400
    assert response.json() == {'sender': [{'code': 'invalid', 'message': 'Sender account does not exist'}]}


def test_cannot_create_block_if_sender_balance_is_not_enough(
    sender_key_pair, sender_account, recipient_account_number, api_client
):
    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': sender_account.balance + 1,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    response = api_client.post('/api/blocks', payload)
    assert response.status_code == 400
    assert response.json() == {
        'amount': [{
            'code': 'invalid',
            'message': 'Amount is greater than sender account balance'
        }]
    }


@pytest.mark.django_db
def test_cannot_create_block_if_sender_and_recipient_are_the_same(sender_key_pair, sender_account, api_client):
    payload = {
        'sender': sender_account.account_number,
        'recipient': sender_account.account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    response = api_client.post('/api/blocks', payload)
    assert response.status_code == 400
    assert response.json() == {
        'non_field_errors': [{
            'code': 'invalid',
            'message': 'Sender and recipient can not be the same'
        }]
    }


@pytest.mark.django_db
def test_cannot_create_block_if_amount_is_none(sender_key_pair, sender_account, recipient_account_number, api_client):
    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': None,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    response = api_client.post('/api/blocks', payload)
    assert response.status_code == 400
    assert response.json() == {'amount': [{'code': 'null', 'message': 'This field may not be null.'}]}


@pytest.mark.django_db
def test_cannot_create_block_if_amount_is_negative(
    sender_key_pair, sender_account, recipient_account_number, api_client
):
    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': -1,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    response = api_client.post('/api/blocks', payload)
    assert response.status_code == 400
    assert response.json() == {
        'amount': [{
            'code': 'min_value',
            'message': 'Ensure this value is greater than or equal to 0.'
        }]
    }


def test_create_block_if_amount_is_zero(sender_key_pair, sender_account, recipient_account_number, api_client):
    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()

    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': 0,
        'payload': {
            'message': 'Hey'
        }
    }
    sign_dict(payload, sender_key_pair.private)
    with patch('core.blocks.views.block.send') as send_mock:
        response = api_client.post('/api/blocks', payload)

    assert response.status_code == 201
    response_json = response.json()
    assert isinstance(response_json.pop('id'), int)
    assert response_json == payload
    query = Block.objects.filter(sender=payload['sender'])
    assert query.count() == 1
    block = query.get()
    assert block.sender == payload['sender']
    assert block.recipient == payload['recipient']
    assert block.amount == payload['amount']
    assert block.payload == payload['payload']
    assert block.signature == payload['signature']

    assert not Account.objects.filter(account_number=recipient_account_number).exists()
    send_mock.assert_called_once_with(dict(payload, id=block.id))


def test_cannot_create_block_with_invalid_signature(
    sender_key_pair, sender_account, recipient_account_number, api_client
):
    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()

    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        },
        'signature': '0' * 128
    }
    with patch('core.blocks.views.block.send') as send_mock:
        response = api_client.post('/api/blocks', payload)

    assert response.status_code == 400
    assert response.json() == {'signature': [{'code': 'invalid', 'message': 'Invalid'}]}

    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()

    send_mock.assert_not_called()


def test_cannot_create_block_without_signature(sender_key_pair, sender_account, recipient_account_number, api_client):
    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()

    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        },
    }
    with patch('core.blocks.views.block.send') as send_mock:
        response = api_client.post('/api/blocks', payload)

    assert response.status_code == 400
    assert response.json() == {'signature': [{'code': 'required', 'message': 'This field is required.'}]}

    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()

    send_mock.assert_not_called()


def test_cannot_update_block(sender_key_pair, sender_account, recipient_account_number, api_client):
    block = baker.make('blocks.Block', sender=sender_account.account_number, recipient='1' * 64)

    payload = {'recipient': '2' * 64}
    response = api_client.patch(f'/api/blocks/{block.id}', payload)
    assert response.status_code == 404
    block.refresh_from_db()
    assert block.recipient == '1' * 64

    payload = {
        'sender': sender_account.account_number,
        'recipient': '2' * 64,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        },
    }
    response = api_client.put(f'/api/blocks/{block.id}', payload)
    assert response.status_code == 404
    block.refresh_from_db()
    assert block.recipient == '1' * 64


@pytest.mark.django_db
def test_list_blocks(api_client):
    response = api_client.get('/api/blocks')
    assert response.status_code == 200
    assert response.json() == []

    block1 = baker.make('blocks.Block')
    block2 = baker.make('blocks.Block')
    block3 = baker.make('blocks.Block')
    response = api_client.get('/api/blocks')
    assert response.status_code == 200
    assert response.json() == [
        {
            'id': block1.id,
            'sender': block1.sender,
            'recipient': block1.recipient,
            'amount': block1.amount,
            'payload': block1.payload,
            'signature': block1.signature,
        },
        {
            'id': block2.id,
            'sender': block2.sender,
            'recipient': block2.recipient,
            'amount': block2.amount,
            'payload': block2.payload,
            'signature': block2.signature,
        },
        {
            'id': block3.id,
            'sender': block3.sender,
            'recipient': block3.recipient,
            'amount': block3.amount,
            'payload': block3.payload,
            'signature': block3.signature,
        },
    ]
