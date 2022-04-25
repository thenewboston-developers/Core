import pytest
from model_bakery import baker

from core.accounts.models import Account
from core.blocks.models import Block


def test_create_block(sender_account, recipient_account_number, api_client):
    assert not Block.objects.exists()
    assert not Account.objects.filter(account_number=recipient_account_number).exists()

    payload = {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        }
    }
    response = api_client.post('/api/blocks', payload)
    assert response.status_code == 201
    response_json = response.json()
    assert isinstance(response_json.pop('id'), int)
    assert response_json == {
        'sender': sender_account.account_number,
        'recipient': recipient_account_number,
        'amount': 5,
        'payload': {
            'message': 'Hey'
        },
    }
    query = Block.objects.filter(sender=payload['sender'])
    assert query.count() == 1
    block = query.get()
    assert block.sender == payload['sender']
    assert block.recipient == payload['recipient']
    assert block.amount == payload['amount']
    assert block.payload == payload['payload']

    recipient_account = Account.objects.get(account_number=recipient_account_number)
    assert recipient_account.balance == 5


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
        },
        {
            'id': block2.id,
            'sender': block2.sender,
            'recipient': block2.recipient,
            'amount': block2.amount,
            'payload': block2.payload,
        },
        {
            'id': block3.id,
            'sender': block3.sender,
            'recipient': block3.recipient,
            'amount': block3.amount,
            'payload': block3.payload,
        },
    ]
