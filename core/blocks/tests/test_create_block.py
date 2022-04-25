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
