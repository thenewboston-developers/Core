import pytest

from core.blocks.models import Block


@pytest.mark.django_db
def test_retrieve_account(sender_account, api_client):
    assert not Block.objects.exists()

    payload = {
        'sender': sender_account.account_number,
        'recipient': 'dd8a4c42ece012b528dda5f469a4706d24459e2eee5a867ff5394cf869466bbe',
        'amount': 5,
        'payload': {
            'message': 'Hey'
        }
    }
    response = api_client.get(f'/api/accounts/{sender_account.account_number}', payload)
    assert response.status_code == 200
    assert response.json() == {
        'account_number': sender_account.account_number,
        'avatar': sender_account.avatar,
        'balance': sender_account.balance,
        'display_name': sender_account.display_name,
    }
