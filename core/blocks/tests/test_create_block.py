import pytest

from core.blocks.models import Block


@pytest.mark.django_db
def test_create_block(sender_account, api_client):
    assert not Block.objects.exists()

    payload = {
        'sender': sender_account.account_number,
        'recipient': 'dd8a4c42ece012b528dda5f469a4706d24459e2eee5a867ff5394cf869466bbe',
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
        'recipient': 'dd8a4c42ece012b528dda5f469a4706d24459e2eee5a867ff5394cf869466bbe',
        'sender': 'a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f',
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
